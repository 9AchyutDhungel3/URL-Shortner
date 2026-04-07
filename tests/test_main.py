import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app

SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def get_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

# Tests --------------

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "URL Shortener is running"}

def test_shorten_url():
    response = client.post("/shorten", json={"original": "www.sample1.com"})
    assert response.status_code == 200  # check if post request is successful
    data = response.json()
    assert "slug" in data # check if there is a field "slug" in the response json
    slug = data["slug"]
    assert len(slug) == 6 # we had the constraint that the length must be 6 digits for the returned slg
    original = data["original"]
    assert original == "https://www.sample1.com" # see if this field is prooperly reflected 
    click_count =  data["clicks"]
    assert click_count == 0 # initially this must be 0 as this test creates a fresh db entry

# post request on "/shorten" should give error(as would be expected)
def test_shorten_url_missing_field():
    response = client.post("/shorten", json={})
    assert response.status_code == 422

def test_redirect():
    shorten_response = client.post("/shorten", json={"original": "www.sample2.com"})
    assert shorten_response.status_code == 200
    data = shorten_response.json()
    slug = data["slug"]

    response_for_slugurl = client.get(f"/{slug}", follow_redirects=False)
    assert response_for_slugurl.status_code == 307
    assert response_for_slugurl.headers['location'] == "https://www.sample2.com"

def test_redirect_increment_clicks():
    response = client.post("/shorten", json={"original": "www.sample1.com"})
    assert response.status_code == 200
    assert response.json()["clicks"] == 0
    slug = response.json()["slug"]

    # Visit the site twice to increment the "clicks" value
    response = client.get(f"/{slug}")
    response = client.get(f"/{slug}")

    response = client.get(f"/stats/{slug}")
    assert response.json()["clicks"] == 2

def test_redirect_not_found():
    response = client.get("/nonexistingslug", follow_redirects=False)
    assert response.status_code == 404

def test_get_stats():
    # Put some arbitrary data on the database of whose stats we'll checkout below:
    response = client.post("/shorten", json={"original": "www.sample1.com"})
    assert response.status_code == 200  # check if post request is successful
    data = response.json()
    slug = data["slug"]

    # Once we get slug, we can use this to access the stat for the associated entry
    response = client.get(f"/stats/{slug}")
    data = response.json()
    assert data["original"] == "https://www.sample1.com" 
    assert data["clicks"] == 0 # initially this must be 0 as this test creates a fresh db entry
    assert data["last_clicked"] == None # a freshly created slug entry is not accessed 

    # click the link once and load up stats after that to see if values are updated correctly
    client.get(f"/{slug}")
    response = client.get(f"/stats/{slug}")
    data = response.json()
    assert data["clicks"] == 1
    assert data["last_clicked"] != None # once accessed this field cannot be None

def test_getstats_not_found():
    response = client.get("/stats/nonexistingslug", follow_redirects=False)
    assert response.status_code == 404






