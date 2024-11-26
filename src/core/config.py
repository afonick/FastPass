import multiprocessing
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn


class AppSettings(BaseSettings):
    # Настройки приложения
    app_name: str = "Fast Pass API"
    app_port: int = 8000
    app_host: str = 'localhost'
    reload: bool = True
    cpu_count: int | None = None
    jwt_secret: str = "your_super_secret"
    algorithm: str = "HS256"

    # Переменные базы данных из .env
    fstr_db_host: str
    fstr_db_port: int
    fstr_db_login: str
    fstr_db_pass: str
    fstr_db_name: str

    # Свойство для вычисления DSN
    @property
    def postgres_dsn(self) -> PostgresDsn:
        return f"postgresql+asyncpg://{self.fstr_db_login}:{self.fstr_db_pass}@{self.fstr_db_host}:{self.fstr_db_port}/{self.fstr_db_name}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"  # Убедитесь, что .env загружается с правильной кодировкой
        _extra = 'allow'  # Позволяет игнорировать неизвестные параметры


# Загружаем настройки из .env
settings = AppSettings()

# Настройки для запуска Uvicorn
uvicorn_options = {
    "host": settings.app_host,
    "port": settings.app_port,
    "workers": settings.cpu_count or multiprocessing.cpu_count(),
    "reload": settings.reload
}