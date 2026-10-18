import requests

login = requests.post(
    "http://127.0.0.1:8000/auth/login",
    json={
        "email": "authadmin@mugonext.com",
        "password": "MugoDev2026!",
    },
)

print("LOGIN STATUS:", login.status_code)

if login.status_code != 200:
    print(login.text)
    raise SystemExit

token = login.json()["access_token"]

response = requests.get(
    "http://127.0.0.1:8000/forecasts/",
    headers={"Authorization": f"Bearer {token}"},
)

print("FORECAST STATUS:", response.status_code)

if response.status_code != 200:
    print(response.text)
    raise SystemExit

forecasts = response.json()

for forecast in forecasts:
    print(
        f"ID={forecast.get('id')} | "
        f"upload={forecast.get('upload_id')} | "
        f"model={forecast.get('forecast_model')} | "
        f"MAE={forecast.get('mae')} | "
        f"RMSE={forecast.get('rmse')} | "
        f"MAPE={forecast.get('mape')} | "
        f"R2={forecast.get('r_squared')} | "
        f"ACC={forecast.get('accuracy_score')} | "
        f"CONF={forecast.get('confidence_score')} | "
        f"CREATED={forecast.get('created_at')}"
    )
