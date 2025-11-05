"""
Schemas for daily aggregated data (quotes, words, weather).
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field

# Weather schemas
class WeatherData(BaseModel):
    """Weather information schema."""
    temperature: float = Field(description="Temperature in Celcius")
    feels_like: float = Field(description="Feels like temperature")
    humidity: int = Field(description="Humidity percentage")
    description: str = Field(description="Weather description")
    icon: str = Field(description="Weather icon code")
    city: str = Field(description="City name")
    country: str = Field(description="Country code")
    updated_at: datetime

# Quote schemas
class QuoteData(BaseModel):
    """Word of the day schema."""
    word: str
    author: Optional[str] = None
    source: str = Field(description="Source: ollama, api, static")
    generated_at: datetime

# Word of the day schemas
class WordData(BaseModel):
    """Word of the day schema."""
    word: str
    definition: str
    example: Optional[str] = None
    pronunciation: Optional[str] = None
    language: str = Field(description="Language code: en, es, fi")

class MultilingualWord(BaseModel):
    """Multilingual word of the day."""
    english: Optional[WordData] = None
    spanish: Optional[WordData] = None
    finnish: Optional[WordData] = None

# Agregated daily data
class DailyDataResponse(BaseModel):
    """Complete daily dashboard data."""
    date: date
    weather: Optional[WeatherData] = None
    quote: Optional[QuoteData] = None
    words: Optional[MultilingualWord] = None
    cache_age_minutes: Optional[int] = Field(
        default=None,
        description="How old the cached data is"
    )
