from datetime import date

#These are simple objects. They are not DB proxies like entities


class Model:

    def __init__(self, name: str, model_year: 'date', brand_id: str, model_id: str = None):
        self.model_id = model_id
        self.name = name
        self.model_year = model_year
        self.brand_id = brand_id

    def __repr__(self) -> str:
        return(f"model_id: {self.model_id}, name: {self.name}, model_year: {self.model_year}, brand_id: {self.brand_id}")
