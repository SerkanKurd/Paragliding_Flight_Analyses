import argparse
import pandas as pd
import numpy as np
import os
import tensorflow as tf
from tf.keras import layers, models
from sklearn.model_selection import train_test_split


def load_and_preprocess(csv_path):
    # 1) Load
    df = pd.read_csv(csv_path)

    # 2) Drop any rows missing the target
    df = df.dropna(subset=['zone'])

    # 3) Encode target: 'standart'→0, 'thermal'→1
    df['zone_label'] = df['zone'].map({'standart': 0, 'thermal': 1})

    # 4) Select only the numeric feature columns
    feature_cols = [
        'latitude', 'longitude',
        'gps_altitude_m', 'pressure_altitude_m',
        'distance_m', 'speed_km/s',
        'climb_m', 'climb_m(delta)', 'climb_rate_m/s',
        'bearing', 'delta_bearing', 'glide_ratio',
        'elapsed_time',
        'temp', 'pressure', 'humidity', 'dew_point',
        'wind_speed', 'wind_deg'
    ]
    df = df[feature_cols + ['zone_label']].dropna()

    # 5) Split into X (features) and y (labels)
    X = df[feature_cols].to_numpy()
    y = df['zone_label'].to_numpy()
    return X, y


def build_model(input_shape):
    # Normalization layer (will be “adapted” on train data)
    normalizer = layers.Normalization(input_shape=input_shape)

    # Simple feed‑forward binary classifier
    model = models.Sequential([
        normalizer,
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(32, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])

    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    return model, normalizer


def main(args):
    # Load & preprocess
    X, y = load_and_preprocess(args.csv)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=args.test_size,
        random_state=42,
        stratify=y
    )

    # Build model
    model, normalizer = build_model(input_shape=(X_train.shape[1],))

    # Adapt normalization on training data
    normalizer.adapt(X_train)

    # Train
    history = model.fit(
        X_train, y_train,
        validation_split=args.val_split,
        epochs=args.epochs,
        batch_size=args.batch_size,
        verbose=2
    )

    # Evaluate
    loss, acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"\nTest loss: {loss:.4f}")
    print(f"Test accuracy: {acc:.4f}")

    # Save the trained model
    model.save(args.output_model)
    print(f"Model saved to {args.output_model}")


if __name__ == '__main__':
    p = argparse.ArgumentParser(description="Train zone‑prediction model")
    p.add_argument('--csv',           type=str,   default=os.path.join('data', 'flight_data_processed.csv'),
                   help='Path to your processed CSV')
    p.add_argument('--test_size',     type=float, default=0.2,
                   help='Fraction of data to reserve for testing')
    p.add_argument('--val_split',     type=float, default=0.2,
                   help='Fraction of training data to use for validation')
    p.add_argument('--batch_size',    type=int,   default=32)
    p.add_argument('--epochs',        type=int,   default=20)
    p.add_argument('--output_model',  type=str,   default=os.path.join('data', 'zone_model.h5'),
                   help='Where to save the trained model')
    args = p.parse_args()
    main(args)
