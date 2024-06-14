import pandas as pd
import torch
import torch.nn as nn
import pickle

# 定义模型架构（确保与训练时的模型架构一致）
class HousePricePredictor(nn.Module):
    def __init__(self, input_dim):
        super(HousePricePredictor, self).__init__()
        self.fc1 = nn.Linear(input_dim, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.fc4(x)
        return x

# 加载测试数据
test_data = pd.read_csv('test_data/test.csv')

# 去掉 'Id' 列
test_data = test_data.drop(columns=['Id'])

# 加载ColumnTransformer
with open('preprocessor.pkl', 'rb') as f:
    preprocessor = pickle.load(f)

# 只转换测试数据
X_test = preprocessor.transform(test_data)

# 将稀疏矩阵转换为密集矩阵
X_test = X_test.toarray()

# 转换为 PyTorch 张量
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)

# 加载模型
input_dim = X_test.shape[1]
model = HousePricePredictor(input_dim)
model.load_state_dict(torch.load('best_model.pth'))
model.eval()

# 进行预测
with torch.no_grad():
    predictions = model(X_test_tensor).numpy()

# 加载目标变量的 StandardScaler
with open('scaler_y.pkl', 'rb') as f:
    scaler_y = pickle.load(f)

# 反标准化预测值
predictions = scaler_y.inverse_transform(predictions)

# 输出预测结果
predictions = predictions.flatten()
output = pd.DataFrame({'Id': test_data.index + 1461, 'SalePrice': predictions})
output.to_csv('repdictions4.csv', index=False)

print('Predictions saved to predictions.csv')