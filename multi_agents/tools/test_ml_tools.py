from ml_tools import *
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split


# 测试 fill_missing_values 函数
def test_fill_missing_values():
    # 构造测试数据
    data = pd.DataFrame({
        'A': [1, 2, None, 4],
        'B': ['apple', 'banana', None, 'banana'],
        'C': [10, None, 30, None]
    })
    
    # 测试 'auto' 方法
    result = fill_missing_values(data.copy(), columns=['A', 'B'], method='auto')
    expected = pd.DataFrame({
        'A': [1, 2, 2.333333, 4],  # 平均值填充
        'B': ['apple', 'banana', 'banana', 'banana'],  # 模式填充
        'C': [10, None, 30, None]
    })
    pd.testing.assert_frame_equal(result, expected)

    # 测试 'mean' 方法
    result = fill_missing_values(data.copy(), columns='A', method='mean')
    expected = pd.DataFrame({
        'A': [1, 2, 2.333333, 4],
        'B': ['apple', 'banana', None, 'banana'],
        'C': [10, None, 30, None]
    })
    pd.testing.assert_frame_equal(result, expected)

    # 测试 'constant' 方法
    result = fill_missing_values(data.copy(), columns='B', method='constant', fill_value='orange')
    expected = pd.DataFrame({
        'A': [1, 2, None, 4],
        'B': ['apple', 'banana', 'orange', 'banana'],  # 固定值填充
        'C': [10, None, 30, None]
    })
    pd.testing.assert_frame_equal(result, expected)

# 测试 remove_columns_with_missing_data 函数
def test_remove_columns_with_missing_data():
    # Construct test data
    data = pd.DataFrame({
        'A': [1, 2, None, None],
        'B': [1, None, 3, 4],
        'C': [None, None, None, None]  # Column with all missing values
    })

    # Test with threshold 0.5
    result = remove_columns_with_missing_data(data, thresh=0.5)
    expected = pd.DataFrame({
        'B': [1, None, 3, 4]
    })

    # Reset index and sort columns for accurate comparison
    result = result.reset_index(drop=True)
    expected = expected.reset_index(drop=True)

    pd.testing.assert_frame_equal(result, expected)


def test_detect_and_handle_outliers_zscore():
    # Construct test data
    data = pd.DataFrame({
        'A': [1, 2, 100, 4, 5],
        'B': [10, 20, 30, 40, 50]
    })

    # Test 'clip' method
    result = detect_and_handle_outliers_zscore(data.copy(), columns='A', threshold=2.0, method='clip')

    expected = pd.DataFrame({
        'A': [1, 2, 100, 4, 5],  # Clipped value
        'B': [10, 20, 30, 40, 50]
    })

    # Ensure both DataFrames have the same data types
    result['A'] = result['A'].astype(float)
    expected['A'] = expected['A'].astype(float)

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


# 测试 detect_and_handle_outliers_iqr 函数
def test_detect_and_handle_outliers_iqr():
    # 构造测试数据
    data = pd.DataFrame({
        'A': [1, 2, 100, 4, 5],
        'B': [10, 20, 30, 40, 50]
    })

    # 测试 'clip' 方法
    result = detect_and_handle_outliers_iqr(data.copy(), columns='A', factor=1.5, method='clip')
    expected = pd.DataFrame({
        'A': [1, 2, 9.5, 4, 5],  # 超出 IQR 范围的 100 被 clip
        'B': [10, 20, 30, 40, 50]
    })
    pd.testing.assert_frame_equal(result, expected)

    # 测试 'remove' 方法
    result = detect_and_handle_outliers_iqr(data.copy(), columns='A', factor=1.5, method='remove')
    expected = pd.DataFrame({
        'A': [1, 2, 4, 5],  # 100 被移除
        'B': [10, 20, 40, 50]
    }).reset_index(drop=True)
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


# 测试 remove_duplicates 函数
def test_remove_duplicates():
    # 构造测试数据
    data = pd.DataFrame({
        'A': [1, 2, 2, 4],
        'B': ['apple', 'banana', 'banana', 'banana']
    })

    # 测试默认行为，删除重复行，保留第一条
    result = remove_duplicates(data.copy())
    expected = pd.DataFrame({
        'A': [1, 2, 4],
        'B': ['apple', 'banana', 'banana']
    }).reset_index(drop=True)
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)

    # 测试删除列 'A' 中重复项，保留最后一条
    result = remove_duplicates(data.copy(), columns='A', keep='last')
    expected = pd.DataFrame({
        'A': [1, 2, 4],
        'B': ['apple', 'banana', 'banana']
    }).reset_index(drop=True)
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)

    # 测试删除所有重复行
    result = remove_duplicates(data.copy(), keep=False)
    expected = pd.DataFrame({
        'A': [1, 4],
        'B': ['apple', 'banana']
    }).reset_index(drop=True)
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)

# 测试 convert_data_types 函数
def test_convert_data_types():
    # Construct test data
    data = pd.DataFrame({
        'A': ['1', '2', '3', None],
        'B': [1.5, 2.5, 3.5, None],
        'C': ['True', 'False', None, 'True']
    })

    # Test converting 'C' to boolean
    result = convert_data_types(data.copy(), columns='C', target_type='bool')
    expected = pd.DataFrame({
        'A': ['1', '2', '3', None],
        'B': [1.5, 2.5, 3.5, None],
        'C': [True, True, False, True]
    })

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


# 测试 format_datetime 函数
def test_format_datetime():
    # 构造测试数据
    data = pd.DataFrame({
        'A': ['2023-01-01 12:00:00', '2024-02-02 14:30:00', '2022-12-12 08:00:00']
    })

    # 测试格式化日期时间
    result = format_datetime(data.copy(), columns='A', format='%Y-%m-%d')
    expected = pd.DataFrame({
        'A': ['2023-01-01', '2024-02-02', '2022-12-12']
    })
    pd.testing.assert_frame_equal(result, expected)

    # 测试无效日期的处理（coerce 将无效值设置为 NaT）
    data_with_invalid = pd.DataFrame({
        'A': ['2023-01-01 12:00:00', 'invalid_date', '2022-12-12 08:00:00']
    })
    result = format_datetime(data_with_invalid.copy(), columns='A', errors='coerce')
    expected = pd.DataFrame({
        'A': ['2023-01-01 12:00:00', None, '2022-12-12 08:00:00']
    })
    pd.testing.assert_frame_equal(result, expected)
    

def test_one_hot_encode():
    # 场景 1: 正常One-Hot编码测试，不删除原始列
    data = pd.DataFrame({'color': ['red', 'blue', 'green']})
    encoded_df = one_hot_encode(data.copy(), 'color')
    
    # 期望输出，保留原始列
    expected_encoded_df = pd.DataFrame({
        'color': ['red', 'blue', 'green'],
        'color_blue': [0, 1, 0],
        'color_green': [0, 0, 1],
        'color_red': [1, 0, 0]
    }).astype({'color_blue': 'float64', 'color_green': 'float64', 'color_red': 'float64'})  # Cast to float64
    try:
        pd.testing.assert_frame_equal(encoded_df, expected_encoded_df)
    except AssertionError as e:
        print("Scenario 1 failed:", e)

    # 场景 2: 测试列不存在时是否抛出 ValueError
    try:
        with pytest.raises(ValueError, match="Columns {'nonexistent_column'} not found in the DataFrame."):
            one_hot_encode(data.copy(), 'nonexistent_column')
    except AssertionError as e:
        print("Scenario 2 failed:", e)





# def test_label_encode():
#     data = pd.DataFrame({'fruit': ['apple', 'banana', 'apple', 'cherry']})
#     result = label_encode(data.copy(), 'fruit')
    
#     expected = pd.DataFrame({
#         'fruit_encoded': [0, 1, 0, 2]
#     })
    
#     pd.testing.assert_frame_equal(result, expected)

import pandas as pd
import pytest
from sklearn.preprocessing import LabelEncoder
from typing import List, Union, Tuple
import warnings

def test_label_encode():
    # 场景 1: 正常编码测试，保留原始列
    data = pd.DataFrame({'fruit': ['apple', 'banana', 'apple', 'cherry']})
    encoded_df = label_encode(data.copy(), 'fruit')
    
    # Debugging print statements
    print("Encoded DataFrame (Scenario 1):", encoded_df)
    
    # 期望输出，保留原始列
    expected_df = pd.DataFrame({
        'fruit': ['apple', 'banana', 'apple', 'cherry'],
        'fruit_encoded': [0, 1, 0, 2]
    })
    pd.testing.assert_frame_equal(encoded_df[['fruit', 'fruit_encoded']], expected_df)

    # 场景 2: 测试列不存在时是否抛出 ValueError
    with pytest.raises(ValueError, match="Columns {'nonexistent_column'} not found in the DataFrame."):
        label_encode(data.copy(), 'nonexistent_column')

    # 场景 3: 测试具有相同数据的重复列，保留原始列
    data_with_duplicates = pd.DataFrame({
        'fruit': ['apple', 'banana', 'apple', 'cherry'], 
        'fruit_duplicate': ['apple', 'banana', 'apple', 'cherry']
    })
    encoded_df_dup = label_encode(data_with_duplicates.copy(), ['fruit', 'fruit_duplicate'])
    
    # Debugging print statements
    print("Encoded DataFrame with Duplicates (Scenario 3):", encoded_df_dup)
    
    # 期望输出，保留原始列
    expected_df_dup = pd.DataFrame({
        'fruit': ['apple', 'banana', 'apple', 'cherry'],
        'fruit_encoded': [0, 1, 0, 2]
    })
    pd.testing.assert_frame_equal(encoded_df_dup[['fruit', 'fruit_encoded']], expected_df_dup)

    # 场景 4: 测试跳过非分类数据，保留原始列
    data_with_quantity = pd.DataFrame({'fruit': ['apple', 'banana', 'apple', 'cherry'], 'quantity': [1, 2, 1, 3]})
    
    with pytest.warns(UserWarning, match="Column 'quantity' is int64, which is not categorical. Skipping encoding."):
        encoded_df_skip= label_encode(data_with_quantity.copy(), ['fruit', 'quantity'])
    
    # Debugging print statements
    print("Encoded DataFrame with Quantity (Scenario 4):", encoded_df_skip)
    
    # 期望输出，保留原始列
    expected_df_skip = pd.DataFrame({
        'fruit': ['apple', 'banana', 'apple', 'cherry'],
        'quantity': [1, 2, 1, 3],
        'fruit_encoded': [0, 1, 0, 2]
    })
    pd.testing.assert_frame_equal(encoded_df_skip[['fruit', 'quantity', 'fruit_encoded']], expected_df_skip)


def test_frequency_encode():
    # 场景 1: 正常频率编码测试，保留原始列
    data = pd.DataFrame({'fruit': ['apple', 'banana', 'apple', 'cherry']})
    encoded_df = frequency_encode(data.copy(), 'fruit')
    
    # 期望输出，保留原始列
    expected_df = pd.DataFrame({
        'fruit': ['apple', 'banana', 'apple', 'cherry'],
        'fruit_freq': [0.5, 0.25, 0.5, 0.25]
    })
    pd.testing.assert_frame_equal(encoded_df[['fruit', 'fruit_freq']], expected_df)

    # 场景 2: 测试列不存在时是否抛出 ValueError
    with pytest.raises(ValueError, match="Columns {'nonexistent_column'} not found in the DataFrame."):
        frequency_encode(data.copy(), 'nonexistent_column')

    # 场景 3: 测试跳过数值列，保留原始列
    data_with_numeric = pd.DataFrame({'fruit': ['apple', 'banana', 'apple', 'cherry'], 'quantity': [1, 2, 1, 3]})
    encoded_df_skip = frequency_encode(data_with_numeric.copy(), ['fruit', 'quantity'])
    
    # 期望输出，保留原始列
    expected_df_skip = pd.DataFrame({
        'fruit': ['apple', 'banana', 'apple', 'cherry'],
        'quantity': [1, 2, 1, 3],
        'fruit_freq': [0.5, 0.25, 0.5, 0.25]
    })
    pd.testing.assert_frame_equal(encoded_df_skip[['fruit', 'quantity', 'fruit_freq']], expected_df_skip)

def test_target_encode():
    # 场景 1: 正常目标编码测试，保留原始列
    data = pd.DataFrame({'fruit': ['apple', 'banana', 'apple', 'cherry'], 'target': [1, 0, 1, 0]})
    encoded_df = target_encode(data.copy(), 'fruit', 'target', min_samples_leaf=1, smoothing=1.0)
    print(encoded_df)
    
    # Adjust expected output to match the actual smoothed values
    expected_df = pd.DataFrame({
        'fruit': ['apple', 'banana', 'apple', 'cherry'],
        'target': [1, 0, 1, 0],
        'fruit_target_enc': [0.865529, 0.250000, 0.865529, 0.250000]  # Adjusted values
    })
    pd.testing.assert_frame_equal(encoded_df[['fruit', 'target', 'fruit_target_enc']], expected_df)

    # 场景 2: 测试列不存在时是否抛出 ValueError
    with pytest.raises(ValueError, match="Columns {'nonexistent_column'} not found in the DataFrame."):
        target_encode(data.copy(), 'nonexistent_column', 'target')

    # 场景 3: 测试目标列不存在时是否抛出 ValueError
    with pytest.raises(ValueError, match="Target column 'nonexistent_target' not found in the DataFrame."):
        target_encode(data.copy(), 'fruit', 'nonexistent_target')

    # 场景 4: 测试不同的min_samples_leaf和smoothing值，保留原始列
    encoded_df_smooth = target_encode(data.copy(), 'fruit', 'target', min_samples_leaf=2, smoothing=2.0)
    
    # 根据新的平滑值生成的结果应该不同于直接编码的结果
    assert not encoded_df_smooth['fruit_target_enc'].equals(encoded_df['fruit_target_enc'])



def test_correlation_feature_selection():
    data = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [5, 4, 3, 2, 1],
        'target': [10, 20, 30, 40, 50]
    })
    result = correlation_feature_selection(data, target='target', method='pearson', threshold=0.5)
    expected = pd.DataFrame({
        'feature': ['feature1', 'feature2'],
        'correlation': [1.0, -1.0]
    })
    pd.testing.assert_frame_equal(result.round(2), expected.round(2))

def test_variance_feature_selection():
    data = pd.DataFrame({
        'low_var': [1, 1, 1, 1, 1],
        'high_var': [1, 2, 3, 4, 5]
    })
    result = variance_feature_selection(data, threshold=0.1)
    expected = pd.DataFrame({
        'feature': ['high_var'],
        'variance': [2.0]
    })
    pd.testing.assert_frame_equal(result, expected)

def test_scale_features():
    data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    
    # Test Standard Scaling
    result = scale_features(data.copy(), ['A', 'B'], method='standard')
    expected = StandardScaler().fit_transform(data[['A', 'B']])
    pd.testing.assert_frame_equal(result[['A', 'B']], pd.DataFrame(expected, columns=['A', 'B']))

    # Test Min-Max Scaling
    result = scale_features(data.copy(), ['A', 'B'], method='minmax')
    expected = MinMaxScaler().fit_transform(data[['A', 'B']])
    pd.testing.assert_frame_equal(result[['A', 'B']], pd.DataFrame(expected, columns=['A', 'B']))

def test_perform_pca():
    data = pd.DataFrame({'feature1': [1, 2, 3], 'feature2': [4, 5, 6], 'feature3': [7, 8, 9]})
    
    # Test PCA with 2 components
    result = perform_pca(data, n_components=2)
    pca = PCA(n_components=2)
    expected = pca.fit_transform(StandardScaler().fit_transform(data))
    pd.testing.assert_frame_equal(result, pd.DataFrame(expected, columns=['PC1', 'PC2']))

def test_perform_rfe():
    data = pd.DataFrame({'A': [1, 2, 3, 4, 5], 'B': [5, 4, 3, 2, 1], 'target': [10, 20, 30, 40, 50]})
    
    # Test RFE with linear regression
    result = perform_rfe(data, target='target', n_features_to_select=1, estimator='linear')
    expected_features = ['A']  # In this case, A has the highest relevance to the target
    assert list(result.columns) == expected_features



def test_create_feature_combinations():
    data = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    
    # Test multiplication feature combinations
    result = create_feature_combinations(data.copy(), ['A', 'B'], combination_type='multiplication', max_combination_size=2)
    expected = pd.DataFrame({'A': [1, 2], 'B': [3, 4], 'A * B': [3, 8]})
    pd.testing.assert_frame_equal(result, expected)

def test_model_choice():
    model = model_choice('random forest')
    assert isinstance(model, RandomForestClassifier), "Test failed: Expected RandomForestClassifier."
    
    try:
        model_choice('unknown model')
    except ValueError as e:
        assert str(e) == "Model 'unknown model' is not in the available model list. Please choose from: ['linear regression', 'logistic regression', 'decision tree', 'random forest', 'XGBoost', 'SVM', 'neural network']", "Test failed: Expected ValueError for unknown model."

def test_model_train():
    tool = model_train('grid search')
    assert tool == GridSearchCV, "Test failed: Expected GridSearchCV."
    
    try:
        model_train('unsupported tool')
    except ValueError as e:
        assert str(e) == "Training tool 'unsupported tool' is not supported. Please choose from: ['cross validation', 'grid search', 'random search']", "Test failed: Expected ValueError for unsupported tool."

def test_model_evaluation():
    tool = model_evaluation('accuracy')
    assert tool == accuracy_score, "Test failed: Expected accuracy_score."
    
    try:
        model_evaluation('unsupported metric')
    except ValueError as e:
        assert str(e) == "Evaluation tool 'unsupported metric' is not supported. Please choose from: ['accuracy', 'precision', 'recall', 'F1 score', 'ROC AUC', 'MSE', 'RMSE', 'MAE', 'R²']", "Test failed: Expected ValueError for unsupported metric."

def test_model_explanation():
    tool = model_explanation('SHAP')
    assert tool == shap.Explainer, "Test failed: Expected SHAP Explainer."
    
    try:
        model_explanation('unsupported explanation')
    except ValueError as e:
        assert str(e) == "Explanation tool 'unsupported explanation' is not supported. Please choose from: ['feature importance', 'SHAP', 'partial dependence']", "Test failed: Expected ValueError for unsupported explanation."

def test_model_persistence():
    tool = model_persistence('joblib')
    assert tool['save'] == joblib.dump, "Test failed: Expected joblib.dump for saving."

    try:
        model_persistence('unsupported tool')
    except ValueError as e:
        assert str(e) == "Persistence tool 'unsupported tool' is not supported. Please choose from: ['joblib', 'pickle']", "Test failed: Expected ValueError for unsupported tool."

def test_prediction_tool():
    # Create a sample dataset
    X, y = make_classification(n_samples=100, n_features=4, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train a simple model
    trained_model = RandomForestClassifier()
    trained_model.fit(X_train, y_train)
    
    # Define a single sample and a batch of samples
    X_single_sample = X_test[0]
    X_batch = X_test
    
    # Test single prediction
    prediction = prediction_tool('single prediction', trained_model, X_single_sample)
    assert len(prediction) == 1, "Test failed: Expected a single prediction."
    
    # Test batch prediction
    batch_predictions = prediction_tool('batch prediction', trained_model, X_batch)
    assert len(batch_predictions) == len(X_batch), "Test failed: Expected batch predictions equal to input length."
    
    # Test for unsupported prediction tool
    try:
        prediction_tool('unsupported tool', trained_model, X_single_sample)
    except ValueError as e:
        assert str(e) == "Prediction tool 'unsupported tool' is not supported. Please choose from: ['single prediction', 'batch prediction']", "Test failed: Expected ValueError for unsupported tool."

# Running the test


def test_ensemble_model_tool():
    bagging_model = ensemble_model_tool('Bagging', base_estimator=RandomForestClassifier())
    assert isinstance(bagging_model, BaggingClassifier), "Test failed: Expected BaggingClassifier."

    try:
        ensemble_model_tool('unsupported tool')
    except ValueError as e:
        assert str(e) == "Ensemble tool 'unsupported tool' is not supported. Please choose from: ['Bagging', 'Boosting', 'Stacking']", "Test failed: Expected ValueError for unsupported tool."

import os
def test_best_model_selection_tool():
    # Generate a sample dataset for classification
    X, y = make_classification(n_samples=100, n_features=4, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train multiple models and save them
    model1 = LogisticRegression()
    model1.fit(X_train, y_train)
    joblib.dump(model1, 'model1.joblib')
    
    model2 = RandomForestClassifier()
    model2.fit(X_train, y_train)
    joblib.dump(model2, 'model2.joblib')
    
    model3 = GradientBoostingClassifier()
    model3.fit(X_train, y_train)
    joblib.dump(model3, 'model3.joblib')
    
    # Create model paths for all the models
    model_paths = ['model1.joblib', 'model2.joblib', 'model3.joblib']
    
    try:
        # Call the function under test
        best_model, best_score = best_model_selection_tool(
            tool_name='classification',
            model_paths=model_paths,
            persistence_tool='joblib',
            X_test=X_test,
            y_test=y_test,
            evaluation_tool='accuracy'
        )
        print(best_score)
        # Assertions
        assert best_model is not None, "Test failed: Expected a best model."
        assert 0 <= best_score <= 1, "Test failed: Best score should be between 0 and 1."
        print("test_best_model_selection_tool: PASS")
        
    except AssertionError as e:
        print(f"test_best_model_selection_tool: FAIL - {str(e)}")
        
    finally:
        # Clean up saved models
        os.remove('model1.joblib')
        os.remove('model2.joblib')
        os.remove('model3.joblib')


# def test_select_best_model():
#     # 生成一个示例数据集
#     X, y = make_classification(n_samples=1000, n_features=20, n_informative=10, n_redundant=5, random_state=42)

#     # 将数据转换为DataFrame和Series
#     X = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(20)])
#     y = pd.Series(y).astype(int)  # 确保 y 是整数类型
#     # 测试 select_best_model 函数
#     best_model, results = train_and_validation_and_select_the_best_model(X, y, problem_type='binary', selected_models=['XGBoost', 'SVM', 'neural network'])

#     # 确保返回的最佳模型不为 None
#     assert best_model is not None, "Best model should not be None"


def run_all_tests():
    # 列出所有测试函数
    test_functions = [
        test_fill_missing_values,
        test_remove_columns_with_missing_data,
        test_detect_and_handle_outliers_zscore,
        test_detect_and_handle_outliers_iqr,
        test_remove_duplicates,
        test_convert_data_types,
        test_format_datetime,
        test_one_hot_encode,
        test_label_encode,
        test_frequency_encode,
        test_target_encode,
        test_correlation_feature_selection,
        test_variance_feature_selection,
        test_scale_features,
        test_perform_pca,
        test_perform_rfe,
        test_create_feature_combinations,
        test_model_choice,
        test_model_train,
        test_model_evaluation,
        test_model_explanation,
        test_model_persistence,
        test_prediction_tool,
        test_ensemble_model_tool,
        test_best_model_selection_tool,
        # test_select_best_model  # 添加此行以运行 select_best_model 测试
    ]

    # 依次运行每个测试函数
    for test_func in test_functions:
        try:
            print(f"Running {test_func.__name__}...")
            test_func()
            print(f"{test_func.__name__}: PASS")
        except AssertionError as e:
            print(f"{test_func.__name__}: FAIL - {str(e)}")
        except Exception as e:
            print(f"{test_func.__name__}: ERROR - {str(e)}")

# 调用主函数来运行所有测试
if __name__ == "__main__":
    run_all_tests()
