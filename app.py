import aranorm as aranorm

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB, GaussianNB

import pickle

from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

##############################################################################################################
#logistic_reg = pickle.load(open(f'{models_folder}/logistic_reg.pkl', 'rb'))
#svm = pickle.load(open(f'{models_folder}/svm.pkl', 'rb'))
#rf = pickle.load(open(f'{models_folder}/rf.pkl', 'rb'))
#mlp = pickle.load(open(f'{models_folder}/mlp.pkl', 'rb'))
#neu_logistic_reg = pickle.load(open(f'{models_folder}/neu_logistic_reg.pkl', 'rb'))
#neu_mnb = pickle.load(open(f'{models_folder}/neu_mnb.pkl', 'rb'))
#neu_rf = pickle.load(open(f'{models_folder}/neu_rf.pkl', 'rb'))
#neu_mlp = pickle.load(open(f'{models_folder}/neu_mlp.pkl', 'rb'))

models_folder = './models/'
models_folder = models_folder.rstrip('/')

vectorizer = pickle.load(open(f'{models_folder}/vectorizer.pkl', 'rb'))
mnb = pickle.load(open(f'{models_folder}/mnb.pkl', 'rb'))
neu_vectorizer = pickle.load(open(f'{models_folder}/neu_vectorizer.pkl', 'rb'))
neu_svm = pickle.load(open(f'{models_folder}/neu_svm.pkl', 'rb'))


##############################################################################################################

def predict_multi_level(X, neu_vectorizer, neu_clf, vectorizer, clf):
    return clf.predict(vectorizer.transform(X))
    neu_y_pred = neu_clf.predict(neu_vectorizer.transform(X))
    if len(X[neu_y_pred == 'NonNeutral']) > 0:
        y_pred = clf.predict(vectorizer.transform(X[neu_y_pred == 'NonNeutral'])) # classify non neutral into positive or negative
        neu_y_pred[neu_y_pred == 'NonNeutral'] = y_pred
    
    final_y_pred = neu_y_pred
    return final_y_pred

##############################################################################################################

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'input_text' not in request.form:
            flash('No text found!')
            return redirect(request.url)

        text = request.form['input_text']
        text = aranorm.normalize_arabic_text(text)
        
        if text == '':
            return 'Please, write an Arabic sentance. Symbols and non-Arabic characters will be removed from the text....'
                
        predcited_sentiment = predict_multi_level(np.array([text]), neu_vectorizer, neu_svm, vectorizer, mnb)
        predcited_sentiment = str(predcited_sentiment.squeeze())
        
        print(f'text: {text}')
        print("Predicted Sentiment:", predcited_sentiment)
        return predcited_sentiment
    
    return '''<!doctype html>
<title>Sentiment Analysis</title>
<script>
function myFunction()
{
    // clear the output text box from the text
    output_text_box = document.getElementById('output_text');
    output_text_box.innerHTML = '';
   
    var elements = document.getElementsByClassName("formVal");
    var formData = new FormData(); 
    
    for(var i=0; i<elements.length; i++)
    {
        formData.append(elements[i].name, elements[i].value);
    }
    var xmlHttp = new XMLHttpRequest();
        xmlHttp.onreadystatechange = function()
        {
            if(xmlHttp.readyState == 4 && xmlHttp.status == 200)
            {
                response = xmlHttp.responseText;
                output_text_box = document.getElementById('output_text');
                console.log(response);
                output_text_box.innerHTML = response;
            }
        }
        xmlHttp.open("post", "/"); 
        xmlHttp.send(formData); 
}
</script>
<h1>تحليل المشاعر من التغريدات</h1>
<p>مثال: أحب أمي و أبي</p>
<form method=post enctype=multipart/form-data>
  <textarea id="input_text"class='formVal' rows="5" cols="50" type="text" name="input_text" placeholder="التغريدة"></textarea> <br>
  <textarea id="output_text" class='formVal' rows="5" cols="50" type="text" name="output_text" placeholder="المشاعر المتوقعة"></textarea>
  <input type="submit" value="submit_now" onclick="myFunction(); return false;">
</form>

</html>
    '''


if __name__ == '__main__':
    app.run(debug=True)

