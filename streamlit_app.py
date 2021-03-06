######################
# Import libraries
######################
import numpy as np
import pandas as pd
import streamlit as st
import pickle
from PIL import Image
from rdkit import Chem
from rdkit.Chem import Descriptors
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR

######################
# Custom function
######################
## Calculate molecular descriptors
def AromaticProportion(m):
  aromatic_atoms = [m.GetAtomWithIdx(i).GetIsAromatic() for i in range(m.GetNumAtoms())]
  aa_count = []
  for i in aromatic_atoms:
    if i==True:
      aa_count.append(1)
  AromaticAtom = sum(aa_count)
  HeavyAtom = Descriptors.HeavyAtomCount(m)
  AR = AromaticAtom/HeavyAtom
  return AR

def generate(smiles, verbose=False):

    moldata= []
    for elem in smiles:
        mol=Chem.MolFromSmiles(elem)
        moldata.append(mol)

    baseData= np.arange(1,1)
    i=0
    for mol in moldata:

        desc_MolLogP = Descriptors.MolLogP(mol)
        desc_MolWt = Descriptors.MolWt(mol)
        desc_NumRotatableBonds = Descriptors.NumRotatableBonds(mol)
        desc_AromaticProportion = AromaticProportion(mol)

        row = np.array([desc_MolLogP,
                        desc_MolWt,
                        desc_NumRotatableBonds,
                        desc_AromaticProportion])

        if(i==0):
            baseData=row
        else:
            baseData=np.vstack([baseData, row])
        i=i+1

    columnNames=["MolLogP","MolWt","NumRotatableBonds","AromaticProportion"]
    descriptors = pd.DataFrame(data=baseData,columns=columnNames)

    return descriptors

######################
# Page Title
######################

image = Image.open('solubility-logo.jpg')

st.image(image, use_column_width=True)

st.write("""
# Molecular Solubility Prediction Web App

This app predicts the **Solubility (LogS)** values of molecules!

Data obtained from the John S. Delaney. [ESOL:  Estimating Aqueous Solubility Directly from Molecular Structure](https://pubs.acs.org/doi/10.1021/ci034243x). ***J. Chem. Inf. Comput. Sci.*** 2004, 44, 3, 1000-1005.
***
""")


######################
# Input molecules (Side Panel)
######################

st.sidebar.header('User Input Features')

## Read SMILES input
SMILES_input = "NCCCC\nCCC\nCN"

SMILES = st.sidebar.text_area("SMILES input", SMILES_input)
SMILES = "C\n" + SMILES #Adds C as a dummy, first item
SMILES = SMILES.split('\n')

st.header('Input SMILES')
SMILES[1:] # Skips the dummy first item

## Calculate molecular descriptors
st.header('Computed molecular descriptors')
X_desc = generate(SMILES)
X_desc[1:] # Skips the dummy first item

######################
# Pre-built model
######################

st.sidebar.header('Machine learning algorithm')
ml_option = st.sidebar.selectbox('What ML algorithm to use?',
             ('RandomForestRegressor', 'SVR'))

# Reads in saved model
#load_model = pickle.load(open('solubility_model.pkl', 'rb'))

# Random forest
df = pd.read_csv('https://raw.githubusercontent.com/dataprofessor/data/master/delaney_solubility_with_descriptors.csv')
X = df.drop(['logS'], axis=1)
y = df.logS

st.header('Predicted LogS values')

if ml_option == 'RandomForestRegressor':
  st.subheader('Random forest')
  rf = RandomForestRegressor(n_estimators=500, random_state=42)
  rf.fit(X, y)
  prediction = rf.predict(X_desc)
  prediction[1:] # Skips the dummy first item
  
if ml_option == 'SVR':
  st.subheader('Support vector regression')
  svr = SVR()
  svr.fit(X, y)
  prediction_svr = svr.predict(X_desc)
  prediction_svr[1:]
