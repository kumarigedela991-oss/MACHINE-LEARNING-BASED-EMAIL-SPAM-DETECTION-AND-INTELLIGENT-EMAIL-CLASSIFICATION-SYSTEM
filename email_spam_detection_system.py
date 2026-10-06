"""
Machine Learning-Based Email Spam Detection and Intelligent Email Classification System
This system detects spam emails and classifies them using machine learning algorithms.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, confusion_matrix, classification_report, 
                             roc_curve, auc, roc_auc_score)
import warnings
warnings.filterwarnings('ignore')

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

# ============================================================================
# 1. GENERATE SYNTHETIC EMAIL DATASET
# ============================================================================

def generate_email_dataset(n_emails=1000, random_state=42):
    """
    Generate a comprehensive email dataset with multiple features
    """
    np.random.seed(random_state)
    
    # Email features
    data = {
        'Email_ID': range(1, n_emails + 1),
        'Subject_Length': np.random.uniform(5, 100, n_emails),
        'Body_Length': np.random.uniform(50, 5000, n_emails),
        'Number_of_URLs': np.random.poisson(2, n_emails),
        'Number_of_Attachments': np.random.poisson(1, n_emails),
        'Contains_Suspicious_Keywords': np.random.binomial(1, 0.3, n_emails),
        'Sender_Domain_Age_Days': np.random.uniform(1, 5000, n_emails),
        'Sender_Reputation_Score': np.random.uniform(0, 100, n_emails),
        'Contains_HTML': np.random.binomial(1, 0.4, n_emails),
        'Contains_Images': np.random.binomial(1, 0.3, n_emails),
        'Number_of_Recipients': np.random.poisson(3, n_emails),
        'Has_Reply_To_Header': np.random.binomial(1, 0.7, n_emails),
        'Sender_SPF_Valid': np.random.binomial(1, 0.8, n_emails),
        'Sender_DKIM_Valid': np.random.binomial(1, 0.75, n_emails),
        'Word_Frequency_Urgency': np.random.uniform(0, 1, n_emails),
        'Word_Frequency_Money': np.random.uniform(0, 1, n_emails),
        'Word_Frequency_Free': np.random.uniform(0, 1, n_emails),
        'Word_Frequency_Click': np.random.uniform(0, 1, n_emails),
    }
    
    df = pd.DataFrame(data)
    
    # Create target variable: Email Classification (0=Legitimate, 1=Spam)
    # Spam emails typically have certain characteristics
    spam_probability = (
        0.15 * (df['Subject_Length'] > 50).astype(int) +
        0.10 * (df['Number_of_URLs'] > 3).astype(int) +
        0.15 * df['Contains_Suspicious_Keywords'] +
        0.10 * (1 - df['Sender_Domain_Age_Days'] / 5000) +
        0.15 * (1 - df['Sender_Reputation_Score'] / 100) +
        0.10 * (1 - df['Sender_SPF_Valid']) +
        0.10 * (1 - df['Sender_DKIM_Valid']) +
        0.05 * df['Word_Frequency_Urgency'] +
        0.05 * df['Word_Frequency_Money'] +
        0.05 * df['Word_Frequency_Free']
    )
    
    # Add randomness
    df['Is_Spam'] = (spam_probability > np.random.uniform(0, 1, n_emails)).astype(int)
    
    # Ensure reasonable class balance
    spam_count = df['Is_Spam'].sum()
    if spam_count < n_emails * 0.15:
        spam_indices = np.random.choice(df[df['Is_Spam'] == 0].index, 
                                       int(n_emails * 0.2), replace=False)
        df.loc[spam_indices, 'Is_Spam'] = 1
    
    return df

# ============================================================================
# 2. DATA EXPLORATION AND ANALYSIS
# ============================================================================

def explore_email_data(df):
    """
    Perform exploratory data analysis on email dataset
    """
    print("=" * 80)
    print("EMAIL DATASET OVERVIEW")
    print("=" * 80)
    print(f"\nDataset Shape: {df.shape}")
    print(f"Number of Emails: {df.shape[0]}")
    print(f"Number of Features: {df.shape[1]}")
    
    print("\n" + "=" * 80)
    print("CLASS DISTRIBUTION")
    print("=" * 80)
    class_dist = df['Is_Spam'].value_counts()
    print(f"Legitimate Emails: {class_dist[0]} ({class_dist[0]/len(df)*100:.2f}%)")
    print(f"Spam Emails: {class_dist[1]} ({class_dist[1]/len(df)*100:.2f}%)")
    
    print("\n" + "=" * 80)
    print("STATISTICAL SUMMARY")
    print("=" * 80)
    print(df.describe())
    
    print("\n" + "=" * 80)
    print("MISSING VALUES")
    print("=" * 80)
    print(df.isnull().sum())
    
    return class_dist

# ============================================================================
# 3. VISUALIZATION FUNCTIONS
# ============================================================================

def create_class_distribution_plot(class_dist):
    """
    Create visualization of spam vs legitimate email distribution
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Bar chart
    labels = ['Legitimate', 'Spam']
    colors = ['green', 'red']
    ax1.bar(labels, class_dist.values, color=colors, alpha=0.8, edgecolor='black')
    ax1.set_title('Email Distribution: Legitimate vs Spam', fontweight='bold', fontsize=12)
    ax1.set_ylabel('Number of Emails')
    ax1.grid(axis='y', alpha=0.3)
    for i, v in enumerate(class_dist.values):
        ax1.text(i, v + 10, str(v), ha='center', fontweight='bold')
    
    # Pie chart
    ax2.pie(class_dist.values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    ax2.set_title('Percentage Distribution of Email Classes', fontweight='bold', fontsize=12)
    
    plt.suptitle('Email Classification Distribution', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/home/ubuntu/class_distribution.png', dpi=300, bbox_inches='tight')
    print("✓ Class distribution plot saved")
    plt.close()

def create_feature_correlation_plot(df):
    """
    Create correlation heatmap for email features
    """
    plt.figure(figsize=(14, 10))
    
    # Select numeric columns
    numeric_df = df.select_dtypes(include=[np.number])
    correlation_matrix = numeric_df.corr()
    
    sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm',
                center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8})
    
    plt.title('Correlation Matrix: Email Features', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('/home/ubuntu/feature_correlation.png', dpi=300, bbox_inches='tight')
    print("✓ Feature correlation plot saved")
    plt.close()

def create_feature_distribution_comparison(df):
    """
    Compare feature distributions between spam and legitimate emails
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Feature Distribution: Spam vs Legitimate Emails', 
                 fontsize=14, fontweight='bold')
    
    features = ['Subject_Length', 'Body_Length', 'Number_of_URLs', 
                'Sender_Reputation_Score', 'Word_Frequency_Urgency', 'Word_Frequency_Money']
    
    for idx, feature in enumerate(features):
        ax = axes[idx // 3, idx % 3]
        
        legitimate = df[df['Is_Spam'] == 0][feature]
        spam = df[df['Is_Spam'] == 1][feature]
        
        ax.hist(legitimate, bins=20, alpha=0.6, label='Legitimate', color='green', edgecolor='black')
        ax.hist(spam, bins=20, alpha=0.6, label='Spam', color='red', edgecolor='black')
        
        ax.set_title(feature, fontweight='bold')
        ax.set_xlabel('Value')
        ax.set_ylabel('Frequency')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/feature_distribution_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Feature distribution comparison plot saved")
    plt.close()

def create_model_comparison_plot(results):
    """
    Create bar chart comparing model performance metrics
    """
    models = list(results.keys())
    accuracy = [results[model]['Accuracy'] for model in models]
    precision = [results[model]['Precision'] for model in models]
    recall = [results[model]['Recall'] for model in models]
    f1 = [results[model]['F1-Score'] for model in models]
    
    x = np.arange(len(models))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    ax.bar(x - 1.5*width, accuracy, width, label='Accuracy', alpha=0.8, edgecolor='black')
    ax.bar(x - 0.5*width, precision, width, label='Precision', alpha=0.8, edgecolor='black')
    ax.bar(x + 0.5*width, recall, width, label='Recall', alpha=0.8, edgecolor='black')
    ax.bar(x + 1.5*width, f1, width, label='F1-Score', alpha=0.8, edgecolor='black')
    
    ax.set_title('Model Performance Comparison', fontweight='bold', fontsize=14)
    ax.set_ylabel('Score')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend()
    ax.set_ylim([0, 1.1])
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/model_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Model comparison plot saved")
    plt.close()

def create_confusion_matrix_plot(y_test, y_pred, model_name):
    """
    Create confusion matrix visualization
    """
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                xticklabels=['Legitimate', 'Spam'],
                yticklabels=['Legitimate', 'Spam'])
    
    plt.title(f'Confusion Matrix - {model_name}', fontweight='bold', fontsize=12)
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig(f'/home/ubuntu/confusion_matrix_{model_name.lower().replace(" ", "_")}.png', 
                dpi=300, bbox_inches='tight')
    print(f"✓ Confusion matrix plot for {model_name} saved")
    plt.close()

def create_roc_curve_plot(y_test, y_pred_proba, model_name):
    """
    Create ROC curve visualization
    """
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC Curve (AUC = {roc_auc:.3f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'ROC Curve - {model_name}', fontweight='bold', fontsize=12)
    plt.legend(loc="lower right")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'/home/ubuntu/roc_curve_{model_name.lower().replace(" ", "_")}.png', 
                dpi=300, bbox_inches='tight')
    print(f"✓ ROC curve plot for {model_name} saved")
    plt.close()

def create_feature_importance_plot(feature_importance, feature_names):
    """
    Create feature importance visualization
    """
    plt.figure(figsize=(12, 8))
    
    indices = np.argsort(feature_importance)[::-1][:15]  # Top 15 features
    
    plt.bar(range(len(indices)), feature_importance[indices], 
            color='steelblue', alpha=0.8, edgecolor='black')
    plt.xticks(range(len(indices)), 
               [feature_names[i] for i in indices], rotation=45, ha='right')
    
    plt.title('Top 15 Features for Spam Detection', fontweight='bold', fontsize=14)
    plt.ylabel('Importance Score')
    plt.xlabel('Features')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('/home/ubuntu/feature_importance.png', dpi=300, bbox_inches='tight')
    print("✓ Feature importance plot saved")
    plt.close()

def create_precision_recall_plot(results):
    """
    Create precision vs recall comparison plot
    """
    models = list(results.keys())
    precision = [results[model]['Precision'] for model in models]
    recall = [results[model]['Recall'] for model in models]
    
    plt.figure(figsize=(10, 7))
    plt.scatter(recall, precision, s=200, alpha=0.6, edgecolors='black', linewidth=2)
    
    for i, model in enumerate(models):
        plt.annotate(model, (recall[i], precision[i]), fontsize=10, fontweight='bold',
                    xytext=(5, 5), textcoords='offset points')
    
    plt.xlabel('Recall', fontsize=12)
    plt.ylabel('Precision', fontsize=12)
    plt.title('Precision vs Recall Comparison', fontweight='bold', fontsize=14)
    plt.grid(alpha=0.3)
    plt.xlim([0, 1.05])
    plt.ylim([0, 1.05])
    plt.tight_layout()
    plt.savefig('/home/ubuntu/precision_recall_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Precision-recall comparison plot saved")
    plt.close()

# ============================================================================
# 4. MACHINE LEARNING MODEL TRAINING AND EVALUATION
# ============================================================================

def train_and_evaluate_models(X_train, X_test, y_train, y_test, X_train_scaled=None, X_test_scaled=None):
    """
    Train multiple machine learning models and evaluate their performance
    """
    if X_train_scaled is None:
        X_train_scaled = X_train
    if X_test_scaled is None:
        X_test_scaled = X_test
    results = {}
    
    print("\n" + "=" * 80)
    print("MACHINE LEARNING MODEL TRAINING AND EVALUATION")
    print("=" * 80)
    
    # 1. Logistic Regression
    print("\n[1/4] Training Logistic Regression Model...")
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    y_pred_lr = lr_model.predict(X_test)
    y_pred_proba_lr = lr_model.predict_proba(X_test)[:, 1]
    
    results['Logistic Regression'] = {
        'Model': lr_model,
        'Predictions': y_pred_lr,
        'Probabilities': y_pred_proba_lr,
        'Accuracy': accuracy_score(y_test, y_pred_lr),
        'Precision': precision_score(y_test, y_pred_lr),
        'Recall': recall_score(y_test, y_pred_lr),
        'F1-Score': f1_score(y_test, y_pred_lr),
        'AUC': roc_auc_score(y_test, y_pred_proba_lr)
    }
    
    print(f"   Accuracy: {results['Logistic Regression']['Accuracy']:.4f}")
    print(f"   Precision: {results['Logistic Regression']['Precision']:.4f}")
    print(f"   Recall: {results['Logistic Regression']['Recall']:.4f}")
    print(f"   F1-Score: {results['Logistic Regression']['F1-Score']:.4f}")
    
    # 2. Random Forest Classifier
    print("\n[2/4] Training Random Forest Classifier...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)
    y_pred_proba_rf = rf_model.predict_proba(X_test)[:, 1]
    
    results['Random Forest'] = {
        'Model': rf_model,
        'Predictions': y_pred_rf,
        'Probabilities': y_pred_proba_rf,
        'Accuracy': accuracy_score(y_test, y_pred_rf),
        'Precision': precision_score(y_test, y_pred_rf),
        'Recall': recall_score(y_test, y_pred_rf),
        'F1-Score': f1_score(y_test, y_pred_rf),
        'AUC': roc_auc_score(y_test, y_pred_proba_rf),
        'Feature_Importance': rf_model.feature_importances_
    }
    
    print(f"   Accuracy: {results['Random Forest']['Accuracy']:.4f}")
    print(f"   Precision: {results['Random Forest']['Precision']:.4f}")
    print(f"   Recall: {results['Random Forest']['Recall']:.4f}")
    print(f"   F1-Score: {results['Random Forest']['F1-Score']:.4f}")
    
    # 3. Gradient Boosting Classifier
    print("\n[3/4] Training Gradient Boosting Classifier...")
    gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
    gb_model.fit(X_train, y_train)
    y_pred_gb = gb_model.predict(X_test)
    y_pred_proba_gb = gb_model.predict_proba(X_test)[:, 1]
    
    results['Gradient Boosting'] = {
        'Model': gb_model,
        'Predictions': y_pred_gb,
        'Probabilities': y_pred_proba_gb,
        'Accuracy': accuracy_score(y_test, y_pred_gb),
        'Precision': precision_score(y_test, y_pred_gb),
        'Recall': recall_score(y_test, y_pred_gb),
        'F1-Score': f1_score(y_test, y_pred_gb),
        'AUC': roc_auc_score(y_test, y_pred_proba_gb),
        'Feature_Importance': gb_model.feature_importances_
    }
    
    print(f"   Accuracy: {results['Gradient Boosting']['Accuracy']:.4f}")
    print(f"   Precision: {results['Gradient Boosting']['Precision']:.4f}")
    print(f"   Recall: {results['Gradient Boosting']['Recall']:.4f}")
    print(f"   F1-Score: {results['Gradient Boosting']['F1-Score']:.4f}")
    
    # 4. Gaussian Naive Bayes (works with scaled data)
    print("\n[4/4] Training Gaussian Naive Bayes...")
    from sklearn.naive_bayes import GaussianNB
    nb_model = GaussianNB()
    nb_model.fit(X_train_scaled, y_train)
    y_pred_nb = nb_model.predict(X_test_scaled)
    y_pred_proba_nb = nb_model.predict_proba(X_test_scaled)[:, 1]
    
    results['Naive Bayes'] = {
        'Model': nb_model,
        'Predictions': y_pred_nb,
        'Probabilities': y_pred_proba_nb,
        'Accuracy': accuracy_score(y_test, y_pred_nb),
        'Precision': precision_score(y_test, y_pred_nb),
        'Recall': recall_score(y_test, y_pred_nb),
        'F1-Score': f1_score(y_test, y_pred_nb),
        'AUC': roc_auc_score(y_test, y_pred_proba_nb)
    }
    
    print(f"   Accuracy: {results['Naive Bayes']['Accuracy']:.4f}")
    print(f"   Precision: {results['Naive Bayes']['Precision']:.4f}")
    print(f"   Recall: {results['Naive Bayes']['Recall']:.4f}")
    print(f"   F1-Score: {results['Naive Bayes']['F1-Score']:.4f}")
    
    print("\n" + "=" * 80)
    print("MODEL PERFORMANCE SUMMARY")
    print("=" * 80)
    
    summary_df = pd.DataFrame({
        'Model': list(results.keys()),
        'Accuracy': [results[m]['Accuracy'] for m in results.keys()],
        'Precision': [results[m]['Precision'] for m in results.keys()],
        'Recall': [results[m]['Recall'] for m in results.keys()],
        'F1-Score': [results[m]['F1-Score'] for m in results.keys()],
        'AUC': [results[m]['AUC'] for m in results.keys()]
    })
    
    print(summary_df.to_string(index=False))
    
    # Identify best model
    best_model_name = max(results.keys(), key=lambda x: results[x]['F1-Score'])
    print(f"\n✓ Best Performing Model: {best_model_name}")
    print(f"  F1-Score: {results[best_model_name]['F1-Score']:.4f}")
    
    return results, best_model_name

# ============================================================================
# 5. MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function
    """
    print("\n" + "=" * 80)
    print("MACHINE LEARNING-BASED EMAIL SPAM DETECTION SYSTEM")
    print("=" * 80)
    
    # Generate dataset
    print("\n[Step 1] Generating Email Dataset...")
    df = generate_email_dataset(n_emails=1000)
    print(f"✓ Dataset generated with {len(df)} emails and {len(df.columns)} features")
    
    # Explore data
    print("\n[Step 2] Exploring Email Dataset...")
    class_dist = explore_email_data(df)
    
    # Prepare features and target
    print("\n[Step 3] Preparing Data for Model Training...")
    feature_columns = [col for col in df.columns if col not in ['Email_ID', 'Is_Spam']]
    
    X = df[feature_columns]
    y = df['Is_Spam']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"✓ Training set size: {len(X_train)}")
    print(f"✓ Test set size: {len(X_test)}")
    
    # Train models
    print("\n[Step 4] Training Machine Learning Models...")
    results, best_model_name = train_and_evaluate_models(X_train, X_test, y_train, y_test, X_train_scaled, X_test_scaled)
    
    # Generate visualizations
    print("\n[Step 5] Generating Visualizations...")
    print("Creating class distribution plot...")
    create_class_distribution_plot(class_dist)
    
    print("Creating feature correlation plot...")
    create_feature_correlation_plot(df)
    
    print("Creating feature distribution comparison...")
    create_feature_distribution_comparison(df)
    
    print("Creating model comparison plot...")
    create_model_comparison_plot(results)
    
    # Create plots for best model
    best_model_results = results[best_model_name]
    print(f"Creating confusion matrix for {best_model_name}...")
    create_confusion_matrix_plot(y_test, best_model_results['Predictions'], best_model_name)
    
    print(f"Creating ROC curve for {best_model_name}...")
    create_roc_curve_plot(y_test, best_model_results['Probabilities'], best_model_name)
    
    # Feature importance for ensemble models
    if 'Feature_Importance' in best_model_results:
        print(f"Creating feature importance plot for {best_model_name}...")
        create_feature_importance_plot(best_model_results['Feature_Importance'], feature_columns)
    
    print("Creating precision-recall comparison...")
    create_precision_recall_plot(results)
    
    print("\n" + "=" * 80)
    print("EXECUTION COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print("\nGenerated Visualizations:")
    print("  1. class_distribution.png")
    print("  2. feature_correlation.png")
    print("  3. feature_distribution_comparison.png")
    print("  4. model_comparison.png")
    print("  5. confusion_matrix_random_forest.png")
    print("  6. roc_curve_random_forest.png")
    print("  7. feature_importance.png")
    print("  8. precision_recall_comparison.png")
    
    return df, results, best_model_name

if __name__ == "__main__":
    df, results, best_model_name = main()
