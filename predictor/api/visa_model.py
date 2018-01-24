"""This module contains the prediction model for visa applications"""
import os
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


class VisaModel:
    """Machine learning model for visa applications predictions"""

    states = {
        'AK': 'ALASKA',
        'AL': 'ALABAMA',
        'AR': 'ARKANSAS',
        'AS': 'AMERICAN SAMOA',
        'AZ': 'ARIZONA',
        'CA': 'CALIFORNIA',
        'CO': 'COLORADO',
        'CT': 'CONNECTICUT',
        'DC': 'DISTRICT OF COLUMBIA',
        'DE': 'DELAWARE',
        'FL': 'FLORIDA',
        'GA': 'GEORGIA',
        'GU': 'GUAM',
        'HI': 'HAWAII',
        'IA': 'IOWA',
        'ID': 'IDAHO',
        'IL': 'ILLINOIS',
        'IN': 'INDIANA',
        'KS': 'KANSAS',
        'KY': 'KENTUCKY',
        'LA': 'LOUISIANA',
        'MA': 'MASSACHUSETTS',
        'MD': 'MARYLAND',
        'ME': 'MAINE',
        'MI': 'MICHIGAN',
        'MN': 'MINNESOTA',
        'MO': 'MISSOURI',
        'MP': 'NORTHERN MARIANA ISLANDS',
        'MS': 'MISSISSIPPI',
        'MT': 'MONTANA',
        'NA': 'NATIONAL',
        'NC': 'NORTH CAROLINA',
        'ND': 'NORTH DAKOTA',
        'NE': 'NEBRASKA',
        'NH': 'NEW HAMPSHIRE',
        'NJ': 'NEW JERSEY',
        'NM': 'NEW MEXICO',
        'NV': 'NEVADA',
        'NY': 'NEW YORK',
        'OH': 'OHIO',
        'OK': 'OKLAHOMA',
        'OR': 'OREGON',
        'PA': 'PENNSYLVANIA',
        'PR': 'PUERTO RICO',
        'RI': 'RHODE ISLAND',
        'SC': 'SOUTH CAROLINA',
        'SD': 'SOUTH DAKOTA',
        'TN': 'TENNESSEE',
        'TX': 'TEXAS',
        'UT': 'UTAH',
        'VA': 'VIRGINIA',
        'VI': 'VIRGIN ISLANDS',
        'VT': 'VERMONT',
        'WA': 'WASHINGTON',
        'WI': 'WISCONSIN',
        'WV': 'WEST VIRGINIA',
        'WY': 'WYOMING'
    }

    columns = {}

    accuracy = ''

    def __init__(self):
        '''
            Columns:
                case_status: 8
                class_of_admission: 9
                country_of_citzenship: 10
                foreign_worker_info_education: 28
                foreign_worker_info_major: 31
                job_info_work_state: 78
                pw_soc_title: 98
        '''
        print('Preparing data...')

        # Absolute path of the directory
        directory = os.path.dirname(__file__)
        # Absolute path of the file
        filename = os.path.join(directory, 'us_perm_visas.csv')
        # Read file
        dataframe = pd.read_csv(filename, low_memory=False,
                                usecols=[8, 9, 10, 28, 31, 78, 98])

        # Remove rows with empty values
        dataframe.dropna(inplace=True)

        # Remove all withdrawn applications
        dataframe = dataframe[dataframe.case_status != 'Withdrawn']

        # Combine certified-expired and certified applications
        dataframe.loc[dataframe.case_status == 'Certified-Expired',
                      'case_status'] = 'Certified'

        # Transform states
        dataframe['job_info_work_state'].replace(
            self.__class__.states, inplace=True)

        # Set columns data
        self.__class__.columns['class_of_admission'] = dataframe['class_of_admission'].unique().tolist()
        self.__class__.columns['country_of_citizenship'] = dataframe['country_of_citizenship'].unique().tolist()
        self.__class__.columns['foreign_worker_info_education'] = dataframe['foreign_worker_info_education'].unique().tolist()
        self.__class__.columns['foreign_worker_info_major'] = dataframe['foreign_worker_info_major'].unique().tolist()
        self.__class__.columns['job_info_work_state'] = dataframe['job_info_work_state'].unique().tolist()
        self.__class__.columns['pw_soc_title'] = dataframe['pw_soc_title'].unique().tolist()

        # Create encoders
        self.label_binarizer = MultiLabelBinarizer(sparse_output=True)
        self.label_encoder = LabelEncoder()

        # Encode data
        y_values = self.label_encoder.fit_transform(
            dataframe.iloc[:, 0].values)
        x_values = self.label_binarizer.fit_transform(
            dataframe.iloc[:, 1:].values)

        # Split training and test data
        x_train, x_test, y_train, y_test = train_test_split(
            x_values, y_values, test_size=0.3, random_state=0)

        # Create random forest classifier
        self.clf = RandomForestClassifier(n_estimators=5)

        # Train model
        print('Training model...')
        self.clf.fit(x_train, y_train)
        print('Finished training model')
        self.__class__.accuracy = self.clf.score(x_test, y_test)
        print('Model accuracy: ' + str(self.__class__.accuracy))

    def predict(self,prediction_data):
        """Predicts the result of a visa application"""
        row = [[
            prediction_data['class_of_admission'],
            prediction_data['country_of_citizenship'],
            prediction_data['foreign_worker_info_education'],
            prediction_data['foreign_worker_info_major'],
            prediction_data['job_info_work_state'],
            prediction_data['pw_soc_title']
        ]]
        encoded_test_row = self.label_binarizer.transform(row)
        prediction = self.clf.predict(encoded_test_row)
        return self.label_encoder.inverse_transform(prediction)
