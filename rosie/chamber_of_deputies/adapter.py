import os

import numpy as np
import pandas as pd
from serenata_toolbox.ceap_dataset import CEAPDataset
from serenata_toolbox.datasets import fetch


class Adapter:
    COMPANIES_DATASET = '2016-09-03-companies.xz'

    def __init__(self, path):
        self.path = path

    @property
    def dataset(self):
        self.update_datasets()
        reimbursements = self.get_reimbursements()
        companies = self.get_companies()
        return pd.merge(reimbursements, companies,
                        how='left',
                        left_on='cnpj_cpf',
                        right_on='cnpj')

    def update_datasets(self):
        os.makedirs(self.path, exist_ok=True)
        ceap = CEAPDataset(self.path)
        ceap.fetch()
        ceap.convert_to_csv()
        ceap.translate()
        ceap.clean()
        fetch(self.COMPANIES_DATASET, self.path)

    def get_reimbursements(self):
        dataset = \
            pd.read_csv(os.path.join(self.path, 'reimbursements.xz'),
                        dtype={'applicant_id': np.str,
                               'cnpj_cpf': np.str,
                               'congressperson_id': np.str,
                               'subquota_number': np.str},
                        low_memory=False)
        dataset['issue_date'] = pd.to_datetime(dataset['issue_date'],
                                               errors='coerce')
        return dataset

    def get_companies(self):
        dataset = pd.read_csv(os.path.join(self.path, self.COMPANIES_DATASET),
                              dtype={'cnpj': np.str},
                              low_memory=False)
        dataset['cnpj'] = dataset['cnpj'].str.replace(r'\D', '')
        dataset['situation_date'] = pd.to_datetime(dataset['situation_date'],
                                                   errors='coerce')
        return dataset
