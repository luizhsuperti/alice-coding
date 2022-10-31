import collections

import numpy as np
import pandas as pd

from data_loaders import ConnectionDataWarehouse
from splitter import Splitter

class Preprocess:

    def __init__(self):
        self.db = ConnectionDataWarehouse()
        pass

    def execute(self):
        self.load()
        self.splitting()

    def splitting(self):
        data = pd.read_csv("output/dataset.csv")
        splitter = Splitter(data = data, target_column='upward_change',
                    id_column='member_internal_code',
                    test_size=0.125)
        splitter.split()
        splitter.save()

    def load(self):

        def add_in_dict_ds(row):
            try:
                ds_dict[row['member_internal_code']] = {
                    **ds_dict[row['member_internal_code']],
                    **{
                        row['cid']: 1
                    }
                }
            except:
                ds_dict[row['member_internal_code']] = {row['cid']: 1}

        def add_in_dict_ind(row):
            try:
                ind_dict[row['member_internal_code']] = {
                    **ind_dict[row['member_internal_code']],
                    **{
                        row['indicador']: row['valor']
                    }
                }
            except:
                ind_dict[row['member_internal_code']] = {
                    row['indicador']: row['valor']
                }

        def add_in_dict_fp(row):
            if row['question_text'] in QUESTIONS:
                try:
                    fp_dict[row['member_internal_code']] = {
                        **fp_dict[row['member_internal_code']],
                        **{
                            row['question_text']: row['answer_text']
                        }
                    }
                except:
                    fp_dict[row['member_internal_code']] = {
                        row['question_text']: row['answer_text']
                    }

        df_fp = self.db.run_sql_query('data/queries/df_fp.sql')

        df_ds = self.db.run_sql_query('data/queries/df_ds.sql')

        df_ds2 = self.db.run_sql_query('data/queries/df_ds2.sql')
        df_ds2['cid'] = df_ds2['cid'].apply(lambda x: x[0:3])
        ds_dict = collections.defaultdict()

        df_ds2.apply(lambda row: add_in_dict_ds(row), axis=1)
        df_ds2_row = pd.DataFrame.from_dict(
            ds_dict, orient='index').reset_index(drop=False).rename(
                columns={'index': 'member_internal_code'})
        df_ds2_row = df_ds2_row.merge(df_ds2)

        df_ds2_row.fillna(0, inplace=True)
        df_ds2_row.drop(columns='cid', inplace=True)
        df_ds2_row['is_risk_or_chronic_dis'] = np.where(
            (df_ds2_row['E66'] == 1) | (df_ds2_row['N63'] == 1) |
            (df_ds2_row['I10'] == 1) | (df_ds2_row['E05'] == 1) |
            (df_ds2_row['E11'] == 1) | (df_ds2_row['B24'] == 1) |
            (df_ds2_row['F84'] == 1) | (df_ds2_row['M05'] == 1) |
            (df_ds2_row['Q90'] == 1) | (df_ds2_row['I64'] == 1) |
            (df_ds2_row['I50'] == 1) | (df_ds2_row['N18'] == 1) |
            (df_ds2_row['Z95'] == 1), 1, 0)

        df_ds2_row['is_support_cid'] = np.where(
            (df_ds2_row['E03'] == 1) | (df_ds2_row['E05'] == 1) |
            (df_ds2_row['E06'] == 1) | (df_ds2_row['E07'] == 1) |
            (df_ds2_row['G40'] == 1) | (df_ds2_row['I42'] == 1) |
            (df_ds2_row['I49'] == 1) | (df_ds2_row['I67'] == 1) |
            (df_ds2_row['J41'] == 1) | (df_ds2_row['J42'] == 1) |
            (df_ds2_row['J43'] == 1) | (df_ds2_row['K25'] == 1) |
            (df_ds2_row['K26'] == 1) | (df_ds2_row['K51'] == 1) |
            (df_ds2_row['K70'] == 1) | (df_ds2_row['K73'] == 1) |
            (df_ds2_row['K74'] == 1) | (df_ds2_row['K76'] == 1) |
            (df_ds2_row['D50'] == 1) | (df_ds2_row['D51'] == 1), 1, 0)
        df_ds2_row.drop_duplicates(inplace=True)

        df_minn_imm_df = self.db.run_sql_query(
            'data/queries/df_minn_imm_df.sql')

        df_ind = self.db.run_sql_query('data/queries/df_ind.sql')

        df_ind = df_ind.drop_duplicates(
            subset=['member_internal_code', 'indicador'])
        ind_dict = collections.defaultdict()
        df_ind.apply(lambda row: add_in_dict_ind(row), axis=1)
        df_ind_row = pd.DataFrame.from_dict(
            ind_dict, orient='index').reset_index(drop=False).rename(
                columns={'index': 'member_internal_code'})

        df_ind_row = df_ind_row[[
            'member_internal_code', 'IMC', 'EUROQOL', 'GAD 2', 'PHQ 2', 'MSQ',
            'Sono - SM', 'Atividade física - SM'
        ]]

        df_stat_info = self.db.run_sql_query('data/queries/df_stat_info.sql')

        df_stat_info['is_female'] = np.where(df_stat_info['sex'] == 'FEMALE',
                                             1, 0)

        static_info_df_clean = df_stat_info[[
            'member_internal_code', 'is_female', 'age'
        ]]

        QUESTIONS = [
            'Tem algo te incomodando agora que você gostaria de tratar? {Pode ser alguma dor, desconforto, qualquer coisa!}',
            'Alguém na sua família tem ou teve Outro tipo de Câncer (por favor especifique)? Pode selecionar todas as opções aplicáveis.',
            'Alguém na sua família tem ou teve Câncer de Pulmão? Pode selecionar todas as opções aplicáveis.',
            'Alguém na sua família tem ou teve Câncer de Colon? Pode selecionar todas as opções aplicáveis.',
            'Alguém na sua família tem ou teve Câncer de Estômago? Pode selecionar todas as opções aplicáveis.',
            'Alguém na sua família tem ou teve Câncer de mama? Pode selecionar todas as opções aplicáveis.',
            'Alguém na sua família tem ou teve Doenças reumatológicas (como lupus, artrite reumatoide, espondilite anquilosnate)? Pode selecionar todas as opções aplicáveis.',
            'Alguém na sua família tem ou teve Diabetes? Pode selecionar todas as opções aplicáveis.',
            'Alguém na sua família tem ou teve Pressão alta? Pode selecionar todas as opções aplicáveis.',
            'Alguém na sua família tem ou teve Infarto? Pode selecionar todas as opções aplicáveis.',
            'Alguém na sua família tem ou teve Acidente Vascular Cerebral (AVC ou derrame)? Pode selecionar todas as opções aplicáveis.',
            'Você fuma ou já fumou?',
            'Você usa drogas recreativas (como maconha ou outras drogas sintéticas)? Se sim, quais?'
        ]

        QUESTIONS = [
        'Alguma dessas doenças está presente na sua família: Acidente vascular cerebral (derrame) - Pode selecionar todas as opções aplicáveis.'
        'Alguma dessas doenças está presente na sua família: Câncer de Intestino - Pode selecionar todas as opções aplicáveis.'
        'Alguma dessas doenças está presente na sua família: Câncer de Mama - Pode selecionar todas as opções aplicáveis.'
        'Alguma dessas doenças está presente na sua família: Câncer de pele - Pode selecionar todas as opções aplicáveis.'
        'Alguma dessas doenças está presente na sua família: Diabetes - Pode selecionar todas as opções aplicáveis.'
        'Alguma dessas doenças está presente na sua família: Hipertensão arterial - Pode selecionar todas as opções aplicáveis.'
        'Alguma dessas doenças está presente na sua família: Infarto do miocárdio - Pode selecionar todas as opções aplicáveis.'
        'O que te incomoda em relação à sua saúde?'
        'Qual a sua altura? (em cm)'
        'Qual o seu peso atual? (em kg)'
        'Você fuma ou já fumou?'
        'Você usa drogas recreativas (como maconha ou outras drogas sintéticas)?'
        ]


        fp_dict = collections.defaultdict()
        df_fp.apply(lambda row: add_in_dict_fp(row), axis=1)
        df_fp_row = pd.DataFrame.from_dict(
            fp_dict, orient='index').reset_index(drop=False).rename(
                columns={'index': 'member_internal_code'})
        df_fp_row.fillna(-1, inplace=True)

        # Predisposicoes
        # cancer
        df_fp_row['has_ancestry_cancer'] = np.where(
            (df_fp_row[
                'Alguém na sua família tem ou teve Outro tipo de Câncer (por favor especifique)? Pode selecionar todas as opções aplicáveis.']
             == 'Ninguém')
            & (df_fp_row[
                'Alguém na sua família tem ou teve Câncer de Pulmão? Pode selecionar todas as opções aplicáveis.']
               == 'Ninguém')
            & (df_fp_row[
                'Alguém na sua família tem ou teve Câncer de Colon? Pode selecionar todas as opções aplicáveis.']
               == 'Ninguém')
            & (df_fp_row[
                'Alguém na sua família tem ou teve Câncer de Estômago? Pode selecionar todas as opções aplicáveis.']
               == 'Ninguém')
            & (df_fp_row[
                'Alguém na sua família tem ou teve Câncer de mama? Pode selecionar todas as opções aplicáveis.']
               == 'Ninguém'), 0, 1)

        df_fp_row.loc[
            (df_fp_row[
                'Alguém na sua família tem ou teve Outro tipo de Câncer (por favor especifique)? Pode selecionar todas as opções aplicáveis.']
             == -1)
            | (df_fp_row[
                'Alguém na sua família tem ou teve Câncer de Pulmão? Pode selecionar todas as opções aplicáveis.']
               == -1)
            | (df_fp_row[
                'Alguém na sua família tem ou teve Câncer de Colon? Pode selecionar todas as opções aplicáveis.']
               == -1)
            | (df_fp_row[
                'Alguém na sua família tem ou teve Câncer de Estômago? Pode selecionar todas as opções aplicáveis.']
               == -1)
            | (df_fp_row[
                'Alguém na sua família tem ou teve Câncer de mama? Pode selecionar todas as opções aplicáveis.']
               == -1), 'has_ancestry_cancer'] = -1

        # rheumatological
        df_fp_row['has_ancestry_rheum'] = np.where((df_fp_row[
            'Alguém na sua família tem ou teve Doenças reumatológicas (como lupus, artrite reumatoide, espondilite anquilosnate)? Pode selecionar todas as opções aplicáveis.']
                                                    == 'Ninguém'), 0, 1)

        df_fp_row.loc[(df_fp_row[
            'Alguém na sua família tem ou teve Doenças reumatológicas (como lupus, artrite reumatoide, espondilite anquilosnate)? Pode selecionar todas as opções aplicáveis.']
                       == -1), 'has_ancestry_rheum'] = -1

        # diabetes
        df_fp_row['has_ancestry_diabetes'] = np.where((df_fp_row[
            'Alguém na sua família tem ou teve Diabetes? Pode selecionar todas as opções aplicáveis.']
                                                       == 'Ninguém'), 0, 1)

        df_fp_row.loc[(df_fp_row[
            'Alguém na sua família tem ou teve Diabetes? Pode selecionar todas as opções aplicáveis.']
                       == -1), 'has_ancestry_diabetes'] = -1

        # blood_pressure
        df_fp_row['has_ancestry_blood_pressure'] = np.where((df_fp_row[
            'Alguém na sua família tem ou teve Pressão alta? Pode selecionar todas as opções aplicáveis.']
                                                             == 'Ninguém'), 0,
                                                            1)

        df_fp_row.loc[(df_fp_row[
            'Alguém na sua família tem ou teve Pressão alta? Pode selecionar todas as opções aplicáveis.']
                       == -1), 'has_ancestry_blood_pressure'] = -1

        # heart_attack
        df_fp_row['has_ancestry_heart_attack'] = np.where((df_fp_row[
            'Alguém na sua família tem ou teve Infarto? Pode selecionar todas as opções aplicáveis.']
                                                           == 'Ninguém'), 0, 1)

        df_fp_row.loc[(df_fp_row[
            'Alguém na sua família tem ou teve Infarto? Pode selecionar todas as opções aplicáveis.']
                       == -1), 'has_ancestry_heart_attack'] = -1

        # Incomodo
        df_fp_row['incomodo_skew'] = df_fp_row[
            'Tem algo te incomodando agora que você gostaria de tratar? {Pode ser alguma dor, desconforto, qualquer coisa!}'].apply(
                lambda x: str(x)[0:3])
        df_fp_row['tem_incomodo_p_tratar'] = df_fp_row['incomodo_skew'].apply(
            lambda x: 1 if x == 'Sim' else (0 if x == 'Não' else x))
        df_fp_row['tem_incomodo_p_tratar'] = pd.to_numeric(
            df_fp_row['tem_incomodo_p_tratar'], errors='coerce')

        # Fumo
        df_fp_row['smoke'] = df_fp_row['Você fuma ou já fumou?'].apply(
            lambda x: str(x).partition('@')[0])
        df_fp_row.loc[df_fp_row['smoke'] == "Nunca fumei", ['smoke']] = "0"
        df_fp_row.loc[df_fp_row['smoke'] ==
                      'Já fumei, mas atualmente não fumo', ['smoke']] = "1"
        df_fp_row.loc[df_fp_row['smoke'] == 'Fumo e tenho intenção de parar',
                      ['smoke']] = "1"
        df_fp_row.loc[df_fp_row['smoke'] ==
                      'Fumo e não tenho intenção de parar', ['smoke']] = "1"

        df_fp_row['smoke'] = pd.to_numeric(df_fp_row['smoke'], errors='coerce')

        # drogas
        df_fp_row['drug'] = df_fp_row[
            'Você usa drogas recreativas (como maconha ou outras drogas sintéticas)? Se sim, quais?'].apply(
                lambda x: str(x).partition('@')[0])
        df_fp_row.loc[df_fp_row['drug'] == "Não uso", ['drug']] = 0
        df_fp_row.loc[df_fp_row['drug'] ==
                      'Uso esporadicamente (menos de 1x/mês)', ['drug']] = 1
        df_fp_row.loc[df_fp_row['drug'] == 'Uso semanalmente ou diariamente',
                      ['drug']] = 1

        df_fp_row['drug'] = pd.to_numeric(df_fp_row['drug'], errors='coerce')

        # cleaning
        df_fp_row_sanitized = df_fp_row[[
            'member_internal_code', 'has_ancestry_cancer',
            'has_ancestry_rheum', 'has_ancestry_diabetes',
            'has_ancestry_blood_pressure', 'has_ancestry_heart_attack',
            'tem_incomodo_p_tratar', 'smoke', 'drug'
        ]]

        df_risk = df_minn_imm_df.merge(df_ds,
                                       how='left',
                                       on='member_internal_code')
        df_risk['ds_mat_score'] = df_risk['ds_mat_score'].fillna(0)
        df_risk['ds_mat_score_cat'] = df_risk['ds_mat_score_cat'].fillna(0)
        df_risk['upward_change'] = np.where(
            df_risk['risk_class_at_imm'] > df_risk['ds_mat_score_cat'], 1, 0)
        df_risk = df_risk[[
            'member_internal_code', 'risk_class_at_imm', 'ds_mat_score',
            'ds_mat_score_cat', 'upward_change', 'final_mat_imm_score'
        ]]
        df_risk['final_mat_imm_score'] = df_risk['final_mat_imm_score'].fillna(
            -1)

        df_ind_row.rename(columns={
            'EUROQOL': 'euroqol',
            'GAD 2': 'gad_2',
            'IMC': 'imc',
            'PHQ 2': 'phq_2',
            'MSQ': 'msq',
            'Sono - SM': 'sono_sm',
            'Atividade física - SM': 'ativ_fisica'
        },
                          inplace=True)
        # winsorize:
        for col in df_ind_row.drop(columns='member_internal_code'):
            i_99 = np.percentile(
                df_ind_row[df_ind_row[col] != -1][col].dropna().values, 99)
            name = col + '_w'
            df_ind_row[name] = df_ind_row[col].apply(lambda x: i_99
                                                     if x >= i_99 else x)

        df_ind_row = df_ind_row[[
            'member_internal_code', 'euroqol_w', 'gad_2_w', 'phq_2_w', 'imc_w'
        ]]
        df_ind_row.dropna(inplace=True)

        ml_df = df_risk.merge(df_ds2_row,
                              how='left',
                              on='member_internal_code').fillna(0).merge(
                                  static_info_df_clean,
                                  how='inner',
                                  on='member_internal_code').merge(
                                      df_fp_row_sanitized,
                                      how='left',
                                      on='member_internal_code').merge(
                                          df_ind_row,
                                          how='left',
                                          on='member_internal_code')

        features = [
            'member_internal_code', 'upward_change', 'ds_mat_score',
            'is_risk_or_chronic_dis', 'is_female', 'age',
            'has_ancestry_cancer', 'has_ancestry_rheum',
            'has_ancestry_diabetes', 'has_ancestry_blood_pressure',
            'has_ancestry_heart_attack', 'tem_incomodo_p_tratar', 'smoke',
            'drug', 'euroqol_w', 'gad_2_w', 'phq_2_w', 'imc_w'
        ]
        ml_df.dropna(inplace=True)
        ml_df[features].to_csv('output/dataset.csv', index=False)

        return ml_df[features]
