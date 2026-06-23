from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # GitHub webhook secret (you'll set this when registering the webhook)
    github_webhook_secret: str

    # Database connection URL
    database_url: str

    class Config:
        env_file = ".env"


settings = Settings()