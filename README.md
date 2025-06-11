# CSGIS System: A GIS-Enabled Crowdsourcing System for Understanding Perceptions of Built Environments #

**The web application component is live at https://csgis.idi.ntnu.no**

This is the official repository for the CSGIS system, developed as part of a Master's Thesis in Informatics at the Norwegian University of Science and Technology (NTNU).
The CSGIS system is a full-stack web platform for collecting and analyzing public perceptions of built environments using geolocated crowdsourced data, along with several multimodal analysis methods to help in understanding people's perceptions of built environments to ultimately improve social well-being.

---

## Technology Stack

- **Frontend:** React.js (JavaScript)
- **Backend:** Node.js with Express.js
- **Database:** PostgreSQL with PostGIS extension
- **GIS Integration:** ArcGIS JavaScript API (via `esri-loader`)
- **Image Analysis (Python):** DeepLabV3+, SegFormer, Mask2Former, ZenSVI, GroundingDINO
- **Text Analysis (Python):** TextBlob, VADER, BERT, DistilBERT, RoBERTa
- **Deployment of web applicatoin component:** Ubuntu 24.04 with Nginx and PM2

---

## Project Structure

```
csgis-system/
├── backend/
│   ├── analysis/
│   │   ├── image_analysis/
│   │   └── text_analysis/
│   └── server.js
└── frontend/
    ├── public/
    └── src/
```

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/da12345/csgis-system.git
cd csgis-system
```

### 2. Backend Setup

```bash
cd backend
npm install
```

Create a `.env.development` file:

```env
NODE_ENV=development
DATABASE_USER=your_db_user
DATABASE_HOST=localhost
DATABASE_NAME=your_db_name
DATABASE_PASSWORD=your_db_password
DATABASE_PORT=5432
CORS_ORIGIN=http://localhost:3000
REACT_APP_BACKEND_URL=http://localhost:5001
REACT_APP_API_BASE_URL=http://localhost:5001/api
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install
```

Create a `.env.development` file:

```env
REACT_APP_API_BASE_URL=http://localhost:5001/api
```

### 4. Database Setup

Ensure PostgreSQL + PostGIS are installed and running.

```sql
-- In psql or pgAdmin:
CREATE DATABASE your_db_name;
\c your_db_name
CREATE EXTENSION postgis;
```

Apply the schema and seed:

```bash
psql -U your_db_user -d your_db_name -f backend/database/schema.sql
psql -U your_db_user -d your_db_name -f backend/database/seed.sql
```

---

## Running Locally

In **two terminals**:

**Terminal 1 (Backend):**

```bash
cd backend
NODE_ENV=development node server.js
```

**Terminal 2 (Frontend):**

```bash
cd frontend
npm start
```

- Frontend: http://localhost:3000  
- API: http://localhost:5001/api

---

## Production Deployment

Create a `.env.production` in `backend/`:

```env
NODE_ENV=production
DATABASE_USER=your_prod_db_user
DATABASE_HOST=your_prod_db_host
DATABASE_PORT=5432
DATABASE_NAME=your_prod_db_name
DATABASE_PASSWORD=your_prod_db_password
CORS_ORIGIN=https://your-domain.com
REACT_APP_API_BASE_URL=https://your-domain.com/api
REACT_APP_BACKEND_URL=https://your-domain.com
```

Use `pm2` to run the backend, and `nginx` to serve the frontend and reverse-proxy the API.

---

## API Endpoints

- `POST /api/submit` – Submit new location, Likert ratings, text, and optional photo.
- `GET /api/get-locations` – Fetch all location submissions and metadata.
- `GET /uploads/:filename` – Serve uploaded images.

---

## Analysis Modules
Analysis modules are connected to the database, and update values in the database upon execution. In some cases, output directories are generated with output files, and in some cases, the output is printed to the terminal.
Generally, if a .py file is run without any arguments, it is calculated for all applicable records in the database that don't have values for the calculated metric. If it is run with a file name an argument, the script is run for only the given file and results output to the terminal.

To use the analysis files, first update the directory paths of the environment variables, upload, and output folders.

### Text Analysis

- Location: `backend/analysis/text_analysis/`
- Models: TextBlob, VADER, BERT, DistilBERT, RoBERTa
- Outputs:
  - `combined_sentiment_analysis` table
  - Word clouds in `text_analysis/`

### Image Analysis

- Location: `backend/analysis/image_analysis/`
- Scripts:
  - `deeplabv3plus.py`, `segformer.py`, `mask2former.py` (GVI via semantic segmentation)
  - `zensvi_groundingdino.py` (object detection)
- Outputs:
  - `image_analysis` table (GVI)
  - `locations` table (tree/car counts)

---

## Deployment Notes

- URL: [https://csgis.idi.ntnu.no](https://csgis.idi.ntnu.no)
- Environment: Ubuntu 24.04
- Backend: runs on port 5001, managed by `pm2`
- Frontend: built with `npm run build`, served via Nginx
- Nginx: reverse proxies API calls, serves images

---

## Known Issues

- Max upload size is 5MB.
- Map UI is not responsive on smaller screens.
- No admin dashboard.
- Form submission error handling could be improved.

---

## Contributions

This project was developed as part of a master’s thesis. Contributions, suggestions, and forks are welcome.

---

## License

[MIT](LICENSE)
