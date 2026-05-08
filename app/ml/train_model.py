from __future__ import annotations

from pathlib import Path
import datetime

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from imblearn.over_sampling import SMOTE
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder


def load_and_explore_data(csv_path: Path) -> pd.DataFrame:
    """Load earthquake CSV dataset and print basic statistics."""
    print("=" * 60)
    print("LOADING AND EXPLORING DATASET")
    print("=" * 60)
    
    df = pd.read_csv(csv_path)
    
    print(f"Total rows: {len(df):,}")
    print(f"Column names: {list(df.columns)}")
    print("\nFirst 5 rows:")
    print(df.head())
    
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean earthquake data by removing duplicates and null values."""
    print("\n" + "=" * 60)
    print("CLEANING DATA")
    print("=" * 60)
    
    print(f"Original dataset size: {len(df):,}")
    
    # Remove duplicates
    df_clean = df.drop_duplicates()
    print(f"After removing duplicates: {len(df_clean):,}")
    
    # Check for important columns
    required_columns = ['magnitude', 'depth_km', 'longitude', 'latitude']
    missing_cols = [col for col in required_columns if col not in df_clean.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Remove rows with null values in important columns
    df_clean = df_clean.dropna(subset=required_columns)
    print(f"After removing null values in key columns: {len(df_clean):,}")
    
    # Convert numeric columns properly
    for col in required_columns:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Remove any rows where conversion failed
    df_clean = df_clean.dropna(subset=required_columns)
    print(f"After converting to numeric: {len(df_clean):,}")
    
    return df_clean


def prepare_target_variable(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare real earthquake severity target variable."""
    print("\n" + "=" * 60)
    print("PREPARING TARGET VARIABLE")
    print("=" * 60)
    
    # Use real alert column from dataset
    df_clean = df.dropna(subset=['alert'])
    print(f"After removing null alerts: {len(df_clean):,}")
    
    print("Real earthquake alert distribution:")
    alert_counts = df_clean['alert'].value_counts()
    for alert, count in alert_counts.items():
        percentage = (count / len(df_clean)) * 100
        print(f"  {alert}: {count:,} ({percentage:.1f}%)")
    
    return df_clean


def feature_engineering(df: pd.DataFrame) -> tuple[pd.DataFrame, KMeans, LabelEncoder]:
    """Create engineered features including location clustering."""
    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING")
    print("=" * 60)
    
    # A) magnitude_squared
    df['magnitude_squared'] = df['magnitude'] ** 2
    
    # B) depth_category
    def get_depth_category(depth):
        if depth <= 70:
            return "shallow"
        elif depth <= 300:
            return "intermediate"
        else:
            return "deep"
    
    df['depth_category'] = df['depth_km'].apply(get_depth_category)
    
    # C) hour_of_day (extract from timestamp)
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'], errors='coerce')
        df['hour_of_day'] = df['time'].dt.hour
        df = df.dropna(subset=['hour_of_day'])
        df['hour_of_day'] = df['hour_of_day'].astype(int)
    else:
        raise ValueError("No 'time' column found in dataset")
    
    # D) location clustering using KMeans
    print("Training KMeans for location clustering...")
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    kmeans.fit(df[['latitude', 'longitude']])
    df['location_cluster'] = kmeans.predict(df[['latitude', 'longitude']])
    
    # Encode depth_category
    depth_encoder = LabelEncoder()
    df['depth_category_encoded'] = depth_encoder.fit_transform(df['depth_category'])
    
    print(f"Created {df['location_cluster'].nunique()} location clusters")
    print(f"Depth categories: {list(depth_encoder.classes_)}")
    
    return df, kmeans, depth_encoder


def prepare_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Prepare final feature set for training."""
    print("\n" + "=" * 60)
    print("PREPARING FEATURE SET")
    print("=" * 60)
    
    feature_columns = [
        'magnitude',
        'magnitude_squared',
        'depth_km',
        'latitude',
        'longitude',
        'hour_of_day',
        'depth_category_encoded',
        'location_cluster'
    ]
    
    # Check if all features exist
    missing_features = [col for col in feature_columns if col not in df.columns]
    if missing_features:
        raise ValueError(f"Missing feature columns: {missing_features}")
    
    X = df[feature_columns].copy()
    y = df['alert']  # Use real alert column
    
    print(f"Feature matrix shape: {X.shape}")
    print(f"Features used: {feature_columns}")
    
    return X, y


def train_and_evaluate_model(X: pd.DataFrame, y: pd.Series, label_encoder: LabelEncoder) -> tuple[RandomForestClassifier, dict]:
    """Train RandomForest model and evaluate performance."""
    print("\n" + "=" * 60)
    print("TRAINING AND EVALUATING MODEL")
    print("=" * 60)
    
    # Train/test split with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set size: {len(X_train):,}")
    print(f"Test set size: {len(X_test):,}")
    
    # Handle class imbalance with SMOTE (only on training data)
    print("Applying SMOTE to handle class imbalance...")
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    
    print(f"After SMOTE - Training set size: {len(X_train_resampled):,}")
    print("Resampled class distribution:")
    for level, count in pd.Series(y_train_resampled).value_counts().items():
        original_label = label_encoder.inverse_transform([level])[0]
        print(f"  {original_label}: {count}")
    
    # Train RandomForest model
    print("Training RandomForest classifier...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        class_weight="balanced",
        random_state=42
    )
    model.fit(X_train_resampled, y_train_resampled)
    
    # Evaluate on test set
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nTest Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    # Cross-validation
    print("\nCross-validation scores:")
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    print(f"CV Mean: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
    
    # Store metrics for report
    metrics = {
        'accuracy': accuracy,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'classification_report': classification_report(y_test, y_pred, output_dict=True),
        'confusion_matrix': cm
    }
    
    return model, metrics


def save_artifacts(model: RandomForestClassifier, kmeans: KMeans, 
                  depth_encoder: LabelEncoder, label_encoder: LabelEncoder,
                  project_root: Path) -> None:
    """Save all trained models and encoders."""
    print("\n" + "=" * 60)
    print("SAVING ARTIFACTS")
    print("=" * 60)
    
    artifacts = {
        'earthquake_model.pkl': model,
        'location_kmeans.pkl': kmeans,
        'depth_encoder.pkl': depth_encoder,
        'label_encoder.pkl': label_encoder
    }
    
    for filename, artifact in artifacts.items():
        filepath = project_root / filename
        joblib.dump(artifact, filepath)
        print(f"Saved: {filepath}")
    
    print("Location KMeans model saved")


def create_visualizations(y: pd.Series, confusion_matrix: np.ndarray, 
                        project_root: Path) -> None:
    """Create and save visualization charts."""
    print("\n" + "=" * 60)
    print("CREATING VISUALIZATIONS")
    print("=" * 60)
    
    # Create reports directory
    reports_dir = project_root / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # 1) Class distribution chart
    plt.figure(figsize=(10, 6))
    class_counts = y.value_counts()
    sns.barplot(x=class_counts.index, y=class_counts.values)
    plt.title('Earthquake Alert Level Distribution')
    plt.xlabel('Alert Level')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    
    # Add value labels on bars
    for i, v in enumerate(class_counts.values):
        plt.text(i, v + max(class_counts.values) * 0.01, f'{v:,}', 
                ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(reports_dir / 'class_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2) Confusion matrix heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(confusion_matrix, annot=True, fmt='d', cmap='Blues',
                xticklabels=['SAFE', 'WARNING', 'DANGER'],
                yticklabels=['SAFE', 'WARNING', 'DANGER'])
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.tight_layout()
    plt.savefig(reports_dir / 'confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Visualizations saved to: {reports_dir}")


def generate_training_report(df: pd.DataFrame, metrics: dict, 
                           feature_columns: list, project_root: Path,
                           label_encoder: LabelEncoder) -> None:
    """Generate comprehensive training report."""
    print("\n" + "=" * 60)
    print("GENERATING TRAINING REPORT")
    print("=" * 60)
    
    reports_dir = project_root / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    report_path = reports_dir / "training_report.txt"
    
    with open(report_path, 'w') as f:
        f.write("EARTHQUAKE RISK CLASSIFICATION MODEL - TRAINING REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Training Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Dataset Information
        f.write("DATASET INFORMATION\n")
        f.write("-" * 30 + "\n")
        f.write(f"Total Records: {len(df):,}\n")
        f.write(f"Source: EarthquakeData (2015-2024).csv\n")
        f.write(f"Features Used: {len(feature_columns)}\n\n")
        
        # Class Distribution
        f.write("CLASS DISTRIBUTION\n")
        f.write("-" * 30 + "\n")
        class_counts = df['alert'].value_counts()
        for level, count in class_counts.items():
            percentage = (count / len(df)) * 100
            f.write(f"{level}: {count:,} ({percentage:.1f}%)\n")
        f.write("\n")
        
        # Features
        f.write("FEATURES USED\n")
        f.write("-" * 30 + "\n")
        for i, feature in enumerate(feature_columns, 1):
            f.write(f"{i}. {feature}\n")
        f.write("\n")
        
        # Model Performance
        f.write("MODEL PERFORMANCE\n")
        f.write("-" * 30 + "\n")
        f.write(f"Test Accuracy: {metrics['accuracy']:.4f}\n")
        f.write(f"Cross-Validation Mean: {metrics['cv_mean']:.4f} (±{metrics['cv_std']:.4f})\n\n")
        
        # Detailed Classification Report
        f.write("DETAILED CLASSIFICATION REPORT\n")
        f.write("-" * 30 + "\n")
        for class_name in label_encoder.classes_:
            if str(class_name) in metrics['classification_report']:
                class_metrics = metrics['classification_report'][str(class_name)]
                f.write(f"\n{class_name}:\n")
                f.write(f"  Precision: {class_metrics['precision']:.4f}\n")
                f.write(f"  Recall: {class_metrics['recall']:.4f}\n")
                f.write(f"  F1-Score: {class_metrics['f1-score']:.4f}\n")
                f.write(f"  Support: {class_metrics['support']:,}\n")
        
        # Confusion Matrix
        f.write("\n\nCONFUSION MATRIX\n")
        f.write("-" * 30 + "\n")
        f.write("Predicted ->\n")
        f.write("Actual |")
        for label in label_encoder.classes_:
            f.write(f"{label:8}")
        f.write("\n")
        for i, row in enumerate(metrics['confusion_matrix']):
            label = label_encoder.classes_[i]
            f.write(f"{label:7}|")
            for val in row:
                f.write(f"{val:8d}")
            f.write("\n")
    
    print(f"Training report saved to: {report_path}")


def train_model() -> None:
    """Main training pipeline for earthquake risk classification."""
    print("EARTHQUAKE RISK CLASSIFICATION - PRODUCTION TRAINING PIPELINE")
    print("=" * 80)
    
    # Resolve paths
    project_root = Path(__file__).resolve().parents[2]
    data_dir = project_root / "data"
    csv_files = list(data_dir.glob("*.csv"))
    
    if not csv_files:
        raise ValueError(f"No CSV files found in {data_dir}")
    
    csv_path = csv_files[0]  # Use first CSV file found
    print(f"Using dataset: {csv_path}")
    
    # 1) Load and explore data
    df = load_and_explore_data(csv_path)
    
    # 2) Clean data
    df_clean = clean_data(df)
    
    # 3) Prepare target variable using real alerts
    df_clean = prepare_target_variable(df_clean)
    
    # 4) Feature engineering
    df_engineered, kmeans, depth_encoder = feature_engineering(df_clean)
    
    # 5) Prepare features
    X, y = prepare_features(df_engineered)
    
    # 6) Encode target labels (real alerts)
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # 7) Train and evaluate model
    model, metrics = train_and_evaluate_model(X, y_encoded, label_encoder)
    
    # 8) Save artifacts
    save_artifacts(model, kmeans, depth_encoder, label_encoder, project_root)
    
    # 9) Create visualizations
    create_visualizations(y, metrics['confusion_matrix'], project_root)
    
    # 10) Generate training report
    generate_training_report(df_engineered, metrics, list(X.columns), project_root, label_encoder)
    
    print("\n" + "=" * 80)
    print("TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print(f"Models saved in: {project_root}")
    print(f"Reports saved in: {project_root / 'reports'}")


if __name__ == "__main__":
    train_model()
