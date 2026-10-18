
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.forecast import Forecast
from app.models.upload import Upload
from app.models.user import User
from app.services.forecasting.engine import ForecastEngine


class ForecastService:
    """
    Orchestrates the MUGONEXT forecasting pipeline.

    Upload
        -> Load dataset
        -> Validate dataset
        -> Generate forecast
        -> Save forecast
        -> Update upload status
    """

    def __init__(self):
        self.engine = ForecastEngine()

    def generate_forecast(
        self,
        db: Session,
        upload: Upload,
        current_user: User,
        name: str,
        target_column: str,
        date_column: str,
        forecast_periods: int,
        frequency: str = "daily",
        description: str | None = None,
        model: str = "auto",
    ) -> Forecast:

        # =====================================================
        # OWNERSHIP / VALIDATION
        # =====================================================

        if upload.company_id != current_user.company_id:
            raise ValueError(
                "Upload does not belong to the current user's company."
            )

        if upload.deleted_at is not None:
            raise ValueError(
                "Cannot generate a forecast from a deleted upload."
            )

        if not upload.storage_path:
            raise ValueError(
                "Upload does not have a storage path."
            )

        if not upload.validation_passed:
            raise ValueError(
                "Upload has not passed dataset validation."
            )

        started_at = datetime.now(timezone.utc)

        # =====================================================
        # MARK UPLOAD AS PROCESSING
        # =====================================================

        upload.status = "processing"
        upload.progress = 10
        upload.processing_started_at = started_at
        upload.error_message = None

        db.commit()
        db.refresh(upload)

        try:

            # =================================================
            # GENERATE FORECAST
            # =================================================

            upload.progress = 25
            db.commit()

            result = self.engine.forecast(
                file_path=upload.storage_path,
                target_column=target_column,
                date_column=date_column,
                forecast_periods=forecast_periods,
                frequency=frequency,
                model=model,
            )

            # =================================================
            # DETERMINE FORECAST DATES
            # =================================================

            forecast_start_date = None
            forecast_end_date = None

            if result.predictions:

                first_date = result.predictions[0]["date"]
                last_date = result.predictions[-1]["date"]

                forecast_start_date = datetime.fromisoformat(
                    first_date
                ).replace(
                    tzinfo=timezone.utc
                )

                forecast_end_date = datetime.fromisoformat(
                    last_date
                ).replace(
                    tzinfo=timezone.utc
                )

            # =================================================
            # COMPLETION TIME
            # =================================================

            completed_at = datetime.now(timezone.utc)

            processing_seconds = int(
                (
                    completed_at - started_at
                ).total_seconds()
            )

            # =================================================
            # QUALITY SCORE
            #
            # Accuracy is used as the default quality score.
            # =================================================

            quality_score = result.accuracy_score

            # =================================================
            # CREATE FORECAST RECORD
            # =================================================

            forecast = Forecast(

                # -------------------------------------------------
                # OWNERSHIP
                # -------------------------------------------------

                company_id=current_user.company_id,
                user_id=current_user.id,
                upload_id=upload.id,

                # -------------------------------------------------
                # BASIC INFORMATION
                # -------------------------------------------------

                name=name,
                description=description,

                forecast_version=1,

                # -------------------------------------------------
                # MODEL
                # -------------------------------------------------

                forecast_model=result.model,

                target_column=result.target_column,
                date_column=result.date_column,

                forecast_periods=result.forecast_periods,
                frequency=frequency,

                # -------------------------------------------------
                # FORECAST OUTPUT
                # -------------------------------------------------

                predictions=result.predictions,

                confidence_intervals=(
                    result.confidence_intervals
                ),

                # -------------------------------------------------
                # FORECAST DATES
                # -------------------------------------------------

                forecast_start_date=forecast_start_date,
                forecast_end_date=forecast_end_date,

                # -------------------------------------------------
                # STATUS
                # -------------------------------------------------

                status="completed",
                progress=100,

                started_at=started_at,
                completed_at=completed_at,

                processing_time_seconds=(
                    processing_seconds
                ),

                # -------------------------------------------------
                # AI / ENGINE
                # -------------------------------------------------

                ai_provider="local",
                model_version="1.0",

                parameters={
                    "engine": "ForecastEngine",
                    "model": result.model,
                    "requested_model": model,
                    "frequency": frequency,
                },

                # -------------------------------------------------
                # FEATURE IMPORTANCE
                #
                # Can be populated later when the engine exposes
                # model feature importance.
                # -------------------------------------------------

                feature_importance=result.feature_importance,

                # -------------------------------------------------
                # EXPLANATION
                # -------------------------------------------------

                ai_explanation=(
                    f"Forecast generated using the "
                    f"MUGONEXT {result.model} "
                    f"forecasting engine."
                ),

                # -------------------------------------------------
                # FLAGS
                # -------------------------------------------------

                is_active=True,
                is_archived=False,

                # -------------------------------------------------
                # MODEL METRICS
                # -------------------------------------------------

                mae=result.mae,
                mse=result.mse,
                rmse=result.rmse,
                mape=result.mape,
                r_squared=result.r_squared,

                accuracy_score=(
                    result.accuracy_score
                ),

                # -------------------------------------------------
                # CONFIDENCE
                #
                # THIS WAS THE MISSING FIELD.
                # -------------------------------------------------

                confidence_score=(
                    result.confidence_score
                ),

                # -------------------------------------------------
                # QUALITY
                # -------------------------------------------------

                quality_score=quality_score,
            )

            # =================================================
            # SAVE FORECAST
            # =================================================

            db.add(forecast)

            # =================================================
            # UPDATE UPLOAD
            # =================================================

            upload.status = "completed"
            upload.progress = 100
            upload.validation_passed = True
            upload.forecast_generated = True
            upload.is_processed = True

            upload.processing_completed_at = (
                completed_at
            )

            upload.processing_time_seconds = (
                processing_seconds
            )

            db.commit()
            db.refresh(forecast)

            return forecast

        # =====================================================
        # ERROR HANDLING
        # =====================================================

        except Exception as exc:

            db.rollback()

            # Re-fetch upload after rollback.
            failed_upload = (
                db.query(Upload)
                .filter(
                    Upload.id == upload.id
                )
                .first()
            )

            if failed_upload:

                failed_upload.status = "failed"

                failed_upload.error_message = str(
                    exc
                )

                failed_upload.processing_completed_at = (
                    datetime.now(timezone.utc)
                )

                db.commit()

            raise