
import pickle

#with open('winrating.pkl' , 'rb') as f:
  #HW = pickle.load(f)
  #AW = pickle.load(f)
  #D = pickle.load(f)

HW=0
AW=0
D=0

with open('winrating.pkl','wb') as f:
  pickle.dump(HW, f)
  pickle.dump(AW, f)
  pickle.dump(D, f)
