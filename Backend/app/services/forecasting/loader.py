from pathlib import Path

import pandas as pd


SUPPORTED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
}


class DatasetLoader:
    """
    Loads CSV and Excel datasets for MUGONEXT forecasting.
    """

    def load(self, file_path: str | Path) -> pd.DataFrame:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Dataset file not found: {path}"
            )

        extension = path.suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported dataset format: {extension}"
            )

        if extension == ".csv":
            dataframe = pd.read_csv(path)

        elif extension in {".xlsx", ".xls"}:
            dataframe = pd.read_excel(path)

        else:
            raise ValueError(
                f"Unsupported dataset format: {extension}"
            )

        if dataframe.empty:
            raise ValueError(
                "Dataset is empty."
            )

        return dataframe

    def get_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> list[str]:
        return dataframe.columns.tolist()

    def get_shape(
        self,
        dataframe: pd.DataFrame,
    ) -> tuple[int, int]:
        return dataframe.shape
