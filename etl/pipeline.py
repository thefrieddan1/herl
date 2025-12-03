from .base import Extractor, Transformer, Loader

class ETLPipeline:
    def __init__(self, extractor: Extractor, transformer: Transformer, loader: Loader):
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

    def run(self):
        print("Starting ETL Pipeline...")
        
        print("Extracting data...")
        data = self.extractor.extract()
        
        print("Transforming data...")
        transformed_data = self.transformer.transform(data)
        
        print("Loading data...")
        self.loader.load(transformed_data)
        
        print("ETL Pipeline completed successfully.")
