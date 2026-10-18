"""
=========================================================
MUGONEXT
Recommendation Service
=========================================================

Business logic for creating, generating, and managing
recommendations.

Author:
MUGONEXT
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.constants import (
    RecommendationPriority,
    RecommendationStatus,
)

from app.models.forecast import Forecast
from app.models.upload import Upload
from app.models.recommendation import Recommendation

from app.services.recommendations.analyzer import (
    RecommendationAnalyzer,
)

from app.services.recommendations.generator import (
    RecommendationGenerator,
)

from app.services.gemini_service import GeminiService


class RecommendationService:
    """
    Service layer responsible for recommendation
    generation and lifecycle management.
    """

    # =====================================================
    # CREATE
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        *,
        company_id: int,
        user_id: int,
        data: dict,
    ) -> Recommendation:
        """
        Create and persist a recommendation.
        """

        recommendation = Recommendation(
            company_id=company_id,
            user_id=user_id,

            upload_id=data.get("upload_id"),
            forecast_id=data.get("forecast_id"),

            title=data.get("title"),
            category=data.get("category"),
            description=data.get("description"),

            recommendation=data.get("recommendation"),
            reasoning=data.get("reasoning"),

            expected_outcome=data.get("expected_outcome"),
            suggested_action=data.get("suggested_action"),

            priority=data.get("priority"),
            priority_score=data.get("priority_score"),
            impact_score=data.get("impact_score"),
            confidence_score=data.get("confidence_score"),

            estimated_cost=data.get("estimated_cost"),
            estimated_savings=data.get("estimated_savings"),
            estimated_revenue_impact=data.get(
                "estimated_revenue_impact"
            ),
            roi_percentage=data.get("roi_percentage"),

            ai_provider=data.get(
                "ai_provider",
                "local",
            ),

            model_version=data.get(
                "model_version",
                "1.0",
            ),

            parameters=data.get(
                "parameters",
                {},
            ),

            source_data=data.get(
                "source_data",
                {},
            ),

            ai_explanation=data.get(
                "ai_explanation"
            ),

            status=RecommendationStatus.COMPLETED,
            progress=100,

            is_active=True,
            is_archived=False,

            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        db.add(recommendation)
        db.commit()
        db.refresh(recommendation)

        return recommendation

    # =====================================================
    # GENERATE FROM FORECAST
    # =====================================================

    @staticmethod
    def generate_from_forecast(
        db: Session,
        *,
        forecast: Forecast,
        company_id: int,
        user_id: int,
    ) -> Recommendation:
        """
        Generate a recommendation from a completed forecast.

        Flow:

        Forecast
            ↓
        Analyzer
            ↓
        Deterministic Generator
            ↓
        Gemini enrichment
            ↓
        Database
        """

        # -------------------------------------------------
        # OWNERSHIP VALIDATION
        # -------------------------------------------------

        if forecast.company_id != company_id:
            raise ValueError(
                "Forecast does not belong to this company."
            )

        # -------------------------------------------------
        # FORECAST VALIDATION
        # -------------------------------------------------

        if forecast.deleted_at is not None:
            raise ValueError(
                "Cannot generate recommendation from "
                "a deleted forecast."
            )

        if forecast.is_archived:
            raise ValueError(
                "Cannot generate recommendation from "
                "an archived forecast."
            )

        if not forecast.is_active:
            raise ValueError(
                "Cannot generate recommendation from "
                "an inactive forecast."
            )

        # -------------------------------------------------
        # PREDICTION VALIDATION
        # -------------------------------------------------

        predictions = forecast.predictions

        if not predictions:
            raise ValueError(
                "Forecast does not contain predictions."
            )

        # -------------------------------------------------
        # ANALYZE FORECAST
        # -------------------------------------------------

        analyzer = RecommendationAnalyzer()

        analysis = analyzer.analyze(
            predictions=forecast.predictions,
            mape=forecast.mape,
            accuracy_score=forecast.accuracy_score,
            confidence_score=forecast.confidence_score,
            r_squared=forecast.r_squared,
        )

        # -------------------------------------------------
        # GENERATE DETERMINISTIC RECOMMENDATION
        # -------------------------------------------------

        generator = RecommendationGenerator()

        recommendation_data = generator.generate(
            analysis=analysis,
            forecast_id=forecast.id,
            upload_id=forecast.upload_id,
        )

        # -------------------------------------------------
        # GEMINI AI ENRICHMENT
        # -------------------------------------------------

        try:
            gemini_service = GeminiService()

            gemini_explanation = (
                gemini_service.enhance_recommendation(
                    recommendation_data=recommendation_data,
                )
            )

            if gemini_explanation:
                recommendation_data["ai_explanation"] = (
                    gemini_explanation
                )

                recommendation_data["ai_provider"] = (
                    "gemini"
                )

                recommendation_data["model_version"] = (
                    GeminiService.MODEL
                )

        except Exception:
            # Gemini must never break the deterministic
            # MUGONEXT recommendation engine.
            pass

        # -------------------------------------------------
        # SAVE RECOMMENDATION
        # -------------------------------------------------

        recommendation = RecommendationService.create(
            db,
            company_id=company_id,
            user_id=user_id,
            data=recommendation_data,
        )

        # -------------------------------------------------
        # UPDATE UPLOAD
        # -------------------------------------------------

        if forecast.upload_id:

            upload = (
                db.query(Upload)
                .filter(
                    Upload.id == forecast.upload_id,
                    Upload.company_id == company_id,
                )
                .first()
            )

            if upload:
                upload.recommendation_generated = True

                upload.updated_at = (
                    datetime.now(timezone.utc)
                )

                db.commit()

        return recommendation

    # =====================================================
    # GET BY ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        *,
        recommendation_id: int,
        company_id: int,
        include_archived: bool = False,
    ) -> Recommendation | None:
        """
        Retrieve one recommendation belonging
        to the specified company.
        """

        query = (
            db.query(Recommendation)
            .filter(
                Recommendation.id == recommendation_id,
                Recommendation.company_id == company_id,
                Recommendation.deleted_at.is_(None),
            )
        )

        if not include_archived:
            query = query.filter(
                Recommendation.is_archived.is_(False)
            )

        return query.first()

    # =====================================================
    # LIST
    # =====================================================

    @staticmethod
    def list(
        db: Session,
        *,
        company_id: int,
        page: int = 1,
        page_size: int = 20,
        priority: RecommendationPriority | None = None,
        status: RecommendationStatus | None = None,
        category: str | None = None,
        include_archived: bool = False,
    ) -> tuple[list[Recommendation], int]:
        """
        Return paginated recommendations belonging
        to a company.

        Supports:

        - pagination
        - priority filtering
        - status filtering
        - category filtering
        - archived filtering
        """

        query = (
            db.query(Recommendation)
            .filter(
                Recommendation.company_id == company_id,
                Recommendation.deleted_at.is_(None),
            )
        )

        # -------------------------------------------------
        # ARCHIVED FILTER
        # -------------------------------------------------

        if not include_archived:
            query = query.filter(
                Recommendation.is_archived.is_(False)
            )

        # -------------------------------------------------
        # PRIORITY FILTER
        # -------------------------------------------------

        if priority is not None:
            query = query.filter(
                Recommendation.priority == priority
            )

        # -------------------------------------------------
        # STATUS FILTER
        # -------------------------------------------------

        if status is not None:
            query = query.filter(
                Recommendation.status == status
            )

        # -------------------------------------------------
        # CATEGORY FILTER
        # -------------------------------------------------

        if category:
            query = query.filter(
                Recommendation.category == category
            )

        # -------------------------------------------------
        # TOTAL
        # -------------------------------------------------

        total = query.count()

        # -------------------------------------------------
        # PAGINATION
        # -------------------------------------------------

        offset = (page - 1) * page_size

        items = (
            query
            .order_by(
                Recommendation.created_at.desc()
            )
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total

    # =====================================================
    # UPDATE
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        *,
        recommendation: Recommendation,
        data: dict,
    ) -> Recommendation:
        """
        Update recommendation fields.
        """

        for field, value in data.items():

            if hasattr(recommendation, field):

                setattr(
                    recommendation,
                    field,
                    value,
                )

        recommendation.updated_at = (
            datetime.now(timezone.utc)
        )

        db.commit()
        db.refresh(recommendation)

        return recommendation

    # =====================================================
    # ARCHIVE
    # =====================================================

    @staticmethod
    def archive(
        db: Session,
        *,
        recommendation: Recommendation,
    ) -> Recommendation:
        """
        Archive a recommendation.
        """

        recommendation.is_archived = True
        recommendation.is_active = False

        recommendation.status = (
            RecommendationStatus.ARCHIVED
        )

        recommendation.updated_at = (
            datetime.now(timezone.utc)
        )

        db.commit()
        db.refresh(recommendation)

        return recommendation

    # =====================================================
    # RESTORE
    # =====================================================

    @staticmethod
    def restore(
        db: Session,
        *,
        recommendation: Recommendation,
    ) -> Recommendation:
        """
        Restore an archived recommendation.
        """

        recommendation.is_archived = False
        recommendation.is_active = True

        recommendation.status = (
            RecommendationStatus.COMPLETED
        )

        recommendation.updated_at = (
            datetime.now(timezone.utc)
        )

        db.commit()
        db.refresh(recommendation)

        return recommendation

    # =====================================================
    # DELETE
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        *,
        recommendation: Recommendation,
    ) -> Recommendation:
        """
        Soft-delete a recommendation.
        """

        recommendation.deleted_at = (
            datetime.now(timezone.utc)
        )

        recommendation.is_active = False

        recommendation.updated_at = (
            datetime.now(timezone.utc)
        )

        db.commit()
        db.refresh(recommendation)

        return recommendation

    # =====================================================
    # MARK ACTIONED
    # =====================================================

    @staticmethod
    def mark_actioned(
        db: Session,
        *,
        recommendation: Recommendation,
        action_taken: bool,
        action_notes: str | None = None,
    ) -> Recommendation:
        """
        Mark a recommendation as actioned.
        """

        recommendation.action_taken = action_taken

        recommendation.action_notes = action_notes

        recommendation.actioned_at = (
            datetime.now(timezone.utc)
            if action_taken
            else None
        )

        recommendation.updated_at = (
            datetime.now(timezone.utc)
        )

        db.commit()
        db.refresh(recommendation)

        return recommendation