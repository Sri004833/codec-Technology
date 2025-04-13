import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Load and preprocess dataset
df = pd.read_csv("spam.csv", encoding='latin-1')[['v1', 'v2']]
df.columns = ['label', 'text']
df['label_num'] = df['label'].map({'ham': 0, 'spam': 1})

# Split data
X_train, X_test, y_train, y_test = train_test_split(df['text'], df['label_num'], test_size=0.2, random_state=42)

# Use TF-IDF for text vectorization
vectorizer = TfidfVectorizer(stop_words='english')
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train SVM model
model = LinearSVC()
model.fit(X_train_vec, y_train)

# Evaluate
y_pred = model.predict(X_test_vec)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Save model and vectorizer
joblib.dump(model, "spam_classifier_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

# Function to classify new email
def classify_email(email_text):
    model = joblib.load("spam_classifier_model.pkl")
    vectorizer = joblib.load("vectorizer.pkl")
    vec = vectorizer.transform([email_text])
    prediction = model.predict(vec)[0]
    return "SPAM" if prediction == 1 else "HAM"

# Test
email = "Your Netflix account has been suspended. Update now to continue watching."
print("\nClassified as:", classify_email(email))
