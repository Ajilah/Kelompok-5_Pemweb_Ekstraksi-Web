import os
import re
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup


# ============================================================
# KONFIGURASI
# ============================================================

URL = "https://spotify-top.com/charts/id/weekly"

OUTPUT_CSV = "data/spotify_top_200.csv"

OUTPUT_HTML = "data/spotify_top_200.html"


# ============================================================
# FUNGSI MEMBERSIHKAN ANGKA
# ============================================================

def clean_number(text):
    """
    Mengubah teks angka seperti:
    '10,125,186'
    menjadi:
    10125186
    """

    if not text:
        return None

    text = text.replace(",", "").strip()

    try:
        return int(text)

    except ValueError:
        return None


# ============================================================
# FUNGSI SCRAPING
# ============================================================

def scrape_spotify():

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/154.0 Safari/537.36"
        )
    }

    # --------------------------------------------------------
    # REQUEST KE WEBSITE
    # --------------------------------------------------------

    try:

        response = requests.get(
            URL,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

    except requests.exceptions.Timeout:

        print("ERROR: Request timeout.")

        return None

    except requests.exceptions.ConnectionError:

        print(
            "ERROR: Tidak dapat terhubung ke website."
        )

        return None

    except requests.exceptions.HTTPError as e:

        print(
            f"ERROR HTTP: {e}"
        )

        return None

    except requests.exceptions.RequestException as e:

        print(
            f"ERROR request: {e}"
        )

        return None


    # --------------------------------------------------------
    # PARSING HTML
    # --------------------------------------------------------

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    rows = []


    # --------------------------------------------------------
    # MENCARI BARIS TABEL
    # --------------------------------------------------------

    table_rows = soup.select(
        "table tbody tr"
    )


    if not table_rows:

        print(
            "ERROR: Baris tabel tidak ditemukan."
        )

        return None


    print(
        f"Ditemukan {len(table_rows)} baris."
    )


    # ========================================================
    # LOOPING SETIAP BARIS
    # ========================================================

    for row in table_rows:

        try:

            cells = row.find_all("td")


            # ------------------------------------------------
            # PASTIKAN JUMLAH KOLOM CUKUP
            # ------------------------------------------------

            if len(cells) < 8:

                continue


            # =================================================
            # RANK
            # =================================================

            rank_text = cells[0].get_text(
                " ",
                strip=True
            )

            rank_match = re.search(
                r"\d+",
                rank_text
            )


            if not rank_match:

                continue


            rank = int(
                rank_match.group()
            )


            # =================================================
            # SONG & ARTIST
            # =================================================

            links = cells[2].find_all("a")


            if len(links) >= 2:

                song = links[0].get_text(
                    " ",
                    strip=True
                )


                artists = [

                    link.get_text(
                        " ",
                        strip=True
                    )

                    for link in links[1:]

                ]


                artist = ", ".join(
                    artists
                )


            else:

                song = cells[2].get_text(
                    " ",
                    strip=True
                )

                artist = ""


            # =================================================
            # STREAMS
            # =================================================

            streams_text = cells[3].get_text(
                " ",
                strip=True
            )


            streams_match = re.search(
                r"[\d,]+",
                streams_text
            )


            streams = (

                clean_number(
                    streams_match.group()
                )

                if streams_match

                else None

            )


            # =================================================
            # PEAK
            # =================================================

            peak_text = cells[5].get_text(
                " ",
                strip=True
            )


            peak_match = re.search(
                r"\d+",
                peak_text
            )


            peak = (

                int(
                    peak_match.group()
                )

                if peak_match

                else None

            )


            # =================================================
            # WEEKS
            # =================================================

            weeks_text = cells[6].get_text(
                " ",
                strip=True
            )


            weeks_match = re.search(
                r"\d+",
                weeks_text
            )


            weeks = (

                int(
                    weeks_match.group()
                )

                if weeks_match

                else None

            )


            # =================================================
            # TOTAL STREAMS
            # =================================================

            total_text = cells[7].get_text(
                " ",
                strip=True
            )


            total_match = re.search(
                r"[\d,]+",
                total_text
            )


            total_streams = (

                clean_number(
                    total_match.group()
                )

                if total_match

                else None

            )


            # =================================================
            # MASUKKAN DATA KE LIST
            # =================================================

            rows.append({

                "rank": rank,

                "song": song,

                "artist": artist,

                "streams": streams,

                "peak": peak,

                "weeks": weeks,

                "total_streams": total_streams

            })


        except Exception as e:

            print(
                f"WARNING: Gagal membaca "
                f"satu baris: {e}"
            )

            continue


    return rows


# ============================================================
# FUNGSI TOP 10
# ============================================================

def get_top_10(data, column):
    """
    Mengambil 10 lagu dengan nilai terbesar
    berdasarkan kolom tertentu.
    """

    sorted_data = sorted(

        data,

        key=lambda x: x[column] or 0,

        reverse=True

    )

    return sorted_data[:10]


# ============================================================
# FUNGSI GENERATE HTML
# ============================================================

def generate_html(data):

    """
    Membuat halaman HTML dari data Spotify Top 200.

    Isi halaman:
    - Header
    - Dummy element
    - Statistik
    - Grafik Top 10 Streams
    - Grafik Top 10 Total Streams
    - Tabel Top 200
    - Bootstrap 5
    - Chart.js
    """


    # ========================================================
    # TOP 10 STREAMS
    # ========================================================

    top_streams = get_top_10(
        data,
        "streams"
    )


    # ========================================================
    # TOP 10 TOTAL STREAMS
    # ========================================================

    top_total_streams = get_top_10(
        data,
        "total_streams"
    )


    # ========================================================
    # DATA LABEL CHART
    # ========================================================

    stream_labels = [

        row["song"]

        for row in top_streams

    ]


    stream_values = [

        row["streams"]

        for row in top_streams

    ]


    total_labels = [

        row["song"]

        for row in top_total_streams

    ]


    total_values = [

        row["total_streams"]

        for row in top_total_streams

    ]


    # ========================================================
    # KONVERSI DATA PYTHON → JAVASCRIPT
    # ========================================================

    stream_labels_js = json.dumps(

        stream_labels,

        ensure_ascii=False

    )


    stream_values_js = json.dumps(

        stream_values

    )


    total_labels_js = json.dumps(

        total_labels,

        ensure_ascii=False

    )


    total_values_js = json.dumps(

        total_values

    )


    # ========================================================
    # MEMBUAT BARIS TABEL
    # ========================================================

    html_rows = ""


    # --------------------------------------------------------
    # LOOPING 200 DATA
    # --------------------------------------------------------

    for row in data:

        html_rows += f"""

        <tr>

            <td>
                <strong>
                    {row['rank']}
                </strong>
            </td>

            <td>
                {row['song']}
            </td>

            <td>
                {row['artist']}
            </td>

            <td>
                {row['streams']:,}
            </td>

            <td>
                {row['peak']}
            </td>

            <td>
                {row['weeks']}
            </td>

            <td>
                {row['total_streams']:,}
            </td>

        </tr>

        """


    # ========================================================
    # HTML CONTENT
    # ========================================================

    html_content = f"""
<!DOCTYPE html>

<html lang="id">

<head>

    <meta charset="UTF-8">


    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >


    <title>
        Spotify Top 200 Indonesia
    </title>


    <!-- =================================================
         BOOTSTRAP 5 CDN
         ================================================= -->

    <link
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
        rel="stylesheet"
    >


    <!-- =================================================
         CHART.JS
         ================================================= -->

    <script
        src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js">
    </script>


    <!-- =================================================
         CUSTOM CSS
         ================================================= -->

    <style>


        /* =================================================
           BODY
           ================================================= */

        body {{

            background:
                linear-gradient(
                    135deg,
                    #071e34,
                    #063b5c,
                    #0b5d72
                );

            min-height: 100vh;

            color: white;

            font-family:
                Arial,
                sans-serif;

        }}


        /* =================================================
           CONTAINER
           ================================================= */

        .main-container {{

            max-width: 1400px;

            margin: auto;

        }}


        /* =================================================
           HERO
           ================================================= */

        .hero {{

            position: relative;

            overflow: hidden;

            background:
                rgba(255, 255, 255, 0.08);

            border:
                1px solid
                rgba(255, 255, 255, 0.15);

            border-radius: 25px;

            padding: 45px;

            margin-bottom: 30px;

            backdrop-filter:
                blur(10px);

        }}


        .hero::before {{

            content: "";

            position: absolute;

            width: 180px;

            height: 180px;

            border-radius: 50%;

            background:
                rgba(0, 255, 200, 0.15);

            right: -50px;

            top: -60px;

        }}


        .hero::after {{

            content: "";

            position: absolute;

            width: 120px;

            height: 120px;

            transform:
                rotate(45deg);

            background:
                rgba(0, 180, 255, 0.12);

            left: -40px;

            bottom: -50px;

        }}


        .hero h1 {{

            font-size: 42px;

            font-weight: 800;

        }}


        .hero p {{

            color: #b9d8e8;

        }}


        /* =================================================
           STATISTIC CARD
           ================================================= */

        .stat-card {{

            position: relative;

            overflow: hidden;

            border-radius: 20px;

            padding: 25px;

            background:
                rgba(255,255,255,0.08);

            border:
                1px solid
                rgba(255,255,255,0.12);

            min-height: 140px;

        }}


        .stat-card::after {{

            content: "";

            position: absolute;

            width: 70px;

            height: 70px;

            border-radius: 50%;

            background:
                rgba(0,255,200,0.12);

            right: -20px;

            bottom: -20px;

        }}


        .stat-number {{

            font-size: 30px;

            font-weight: 800;

        }}


        .stat-label {{

            color: #a9c9d8;

            font-size: 14px;

        }}


        /* =================================================
           CHART CARD
           ================================================= */

        .chart-card {{

            background:
                rgba(255,255,255,0.96);

            border-radius: 22px;

            padding: 25px;

            margin-top: 30px;

            color: #102a43;

            box-shadow:
                0 15px 40px
                rgba(0,0,0,0.18);

        }}


        .chart-title {{

            font-weight: 800;

            font-size: 22px;

        }}


        .chart-description {{

            color: #607d8b;

            margin-bottom: 20px;

        }}


        .chart-wrapper {{

            height: 500px;

        }}


        /* =================================================
           TABLE CARD
           ================================================= */

        .table-card {{

            background:
                rgba(255,255,255,0.96);

            color: #102a43;

            border-radius: 22px;

            padding: 25px;

            margin-top: 30px;

        }}


        .table-responsive {{

            border-radius: 15px;

        }}


        .section-title {{

            font-weight: 800;

        }}


    </style>

</head>


<body>


<div class="container-fluid py-5">


<div class="main-container">


    <!-- =================================================
         HERO / HEADER
         ================================================= -->

    <div class="hero">

        <h1>
            Spotify Top 200 Indonesia
        </h1>

        <p class="lead mb-0">

            Weekly Chart Analytics —
            analisis performa lagu berdasarkan
            streams dan total streams.

        </p>

    </div>


    <!-- =================================================
         STATISTIC CARDS
         ================================================= -->

    <div class="row g-4">


        <!-- TOTAL LAGU -->

        <div class="col-md-4">

            <div class="stat-card">

                <div class="stat-label">
                    TOTAL LAGU
                </div>

                <div class="stat-number">
                    {len(data)}
                </div>

                <div class="stat-label">
                    Lagu dalam chart
                </div>

            </div>

        </div>


        <!-- TOP STREAMS -->

        <div class="col-md-4">

            <div class="stat-card">

                <div class="stat-label">
                    #1 STREAMS
                </div>

                <div class="stat-number">

                    {top_streams[0]['streams']:,}

                </div>

                <div class="stat-label">

                    {top_streams[0]['song']}

                </div>

            </div>

        </div>


        <!-- TOP TOTAL STREAMS -->

        <div class="col-md-4">

            <div class="stat-card">

                <div class="stat-label">
                    #1 TOTAL STREAMS
                </div>

                <div class="stat-number">

                    {top_total_streams[0]['total_streams']:,}

                </div>

                <div class="stat-label">

                    {top_total_streams[0]['song']}

                </div>

            </div>

        </div>


    </div>


    <!-- =================================================
         CHART 1
         ================================================= -->

    <div class="chart-card">

        <div class="chart-title">

            Top 10 Lagu Berdasarkan Streams

        </div>


        <div class="chart-description">

            Perbandingan jumlah streams mingguan
            dari 10 lagu dengan performa tertinggi.

        </div>


        <div class="chart-wrapper">

            <canvas
                id="streamsChart">
            </canvas>

        </div>

    </div>


    <!-- =================================================
         CHART 2
         ================================================= -->

    <div class="chart-card">

        <div class="chart-title">

            Top 10 Lagu Berdasarkan Total Streams

        </div>


        <div class="chart-description">

            Perbandingan total streams yang telah
            dikumpulkan selama berada di chart.

        </div>


        <div class="chart-wrapper">

            <canvas
                id="totalStreamsChart">
            </canvas>

        </div>

    </div>


    <!-- =================================================
         TABEL TOP 200
         ================================================= -->

    <div class="table-card">


        <h2 class="section-title mb-4">

            Spotify Top 200

        </h2>


        <div class="table-responsive">


            <table
                class="
                    table
                    table-striped
                    table-hover
                    align-middle
                "
            >


                <thead
                    class="table-dark"
                >

                    <tr>

                        <th>Rank</th>

                        <th>Song</th>

                        <th>Artist</th>

                        <th>Streams</th>

                        <th>Peak</th>

                        <th>Weeks</th>

                        <th>Total Streams</th>

                    </tr>

                </thead>


                <tbody>

                    {html_rows}

                </tbody>


            </table>


        </div>


    </div>


</div>

</div>


<!-- =====================================================
     JAVASCRIPT CHART
     ===================================================== -->

<script>


// ========================================================
// DATA STREAMS
// ========================================================

const streamLabels =
    {stream_labels_js};


const streamValues =
    {stream_values_js};


// ========================================================
// DATA TOTAL STREAMS
// ========================================================

const totalLabels =
    {total_labels_js};


const totalValues =
    {total_values_js};


// ========================================================
// CHART TOP 10 STREAMS
// ========================================================

new Chart(

    document.getElementById(
        "streamsChart"
    ),

    {{

        type: "bar",


        data: {{

            labels:
                streamLabels,


            datasets: [{{

                label:
                    "Streams",


                data:
                    streamValues,


                borderRadius:
                    8,


                borderSkipped:
                    false

            }}]

        }},


        options: {{

            responsive:
                true,


            maintainAspectRatio:
                false,


            indexAxis:
                "y",


            plugins: {{

                legend: {{

                    display:
                        false

                }},


                tooltip: {{

                    callbacks: {{

                        label:
                            function(context) {{

                                return (
                                    context.raw
                                    .toLocaleString(
                                        "id-ID"
                                    )
                                    + " streams"
                                );

                            }}

                    }}

                }}

            }},


            scales: {{

                x: {{

                    beginAtZero:
                        true,


                    ticks: {{

                        callback:
                            function(value) {{

                                return value
                                    .toLocaleString(
                                        "id-ID"
                                    );

                            }}

                    }}

                }}

            }}

        }}

    }}

);


// ========================================================
// CHART TOP 10 TOTAL STREAMS
// ========================================================

new Chart(

    document.getElementById(
        "totalStreamsChart"
    ),

    {{

        type: "bar",


        data: {{

            labels:
                totalLabels,


            datasets: [{{

                label:
                    "Total Streams",


                data:
                    totalValues,


                borderRadius:
                    8,


                borderSkipped:
                    false

            }}]

        }},


        options: {{

            responsive:
                true,


            maintainAspectRatio:
                false,


            indexAxis:
                "y",


            plugins: {{

                legend: {{

                    display:
                        false

                }},


                tooltip: {{

                    callbacks: {{

                        label:
                            function(context) {{

                                return (
                                    context.raw
                                    .toLocaleString(
                                        "id-ID"
                                    )
                                    + " total streams"
                                );

                            }}

                    }}

                }}

            }},


            scales: {{

                x: {{

                    beginAtZero:
                        true,


                    ticks: {{

                        callback:
                            function(value) {{

                                return value
                                    .toLocaleString(
                                        "id-ID"
                                    );

                            }}

                    }}

                }}

            }}

        }}

    }}

);


</script>


</body>

</html>
"""


    # ========================================================
    # SIMPAN HTML
    # ========================================================

    try:

        with open(
            OUTPUT_HTML,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                html_content
            )


        print()

        print(
            "HTML berhasil dibuat:"
        )

        print(
            OUTPUT_HTML
        )


    except OSError as e:

        print(
            f"ERROR saat membuat HTML: {e}"
        )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print(
        "======================================"
    )

    print(
        "   SPOTIFY TOP 200 SCRAPER"
    )

    print(
        "======================================"
    )

    print()

    print(
        "Mulai scraping..."
    )

    print(
        f"URL: {URL}"
    )


    # ========================================================
    # SCRAPING
    # ========================================================

    data = scrape_spotify()


    if data is None:

        print(
            "Scraping gagal."
        )

        return


    # ========================================================
    # FILTER RANK 1-200
    # ========================================================

    data = [

        row

        for row in data

        if 1 <= row["rank"] <= 200

    ]


    # ========================================================
    # SORTING BERDASARKAN RANK
    # ========================================================

    data = sorted(

        data,

        key=lambda x: x["rank"]

    )


    print()

    print(
        f"Data berhasil diambil: "
        f"{len(data)} lagu"
    )


    if len(data) != 200:

        print(
            "WARNING: Data bukan tepat 200 lagu."
        )


    # ========================================================
    # DATAFRAME
    # ========================================================

    df = pd.DataFrame(data)


    columns = [

        "rank",

        "song",

        "artist",

        "streams",

        "peak",

        "weeks",

        "total_streams"

    ]


    df = df[columns]


    # ========================================================
    # BUAT FOLDER DATA
    # ========================================================

    os.makedirs(

        "data",

        exist_ok=True

    )


    # ========================================================
    # SIMPAN CSV
    # ========================================================

    try:

        df.to_csv(

            OUTPUT_CSV,

            index=False,

            encoding="utf-8-sig"

        )


        print()

        print(
            "CSV berhasil dibuat:"
        )

        print(
            OUTPUT_CSV
        )


    except OSError as e:

        print(
            f"ERROR saat menyimpan CSV: {e}"
        )

        return


    # ========================================================
    # TAMPILKAN 5 DATA PERTAMA
    # ========================================================

    print()

    print(
        "5 data pertama:"
    )

    print(
        df.head()
    )


    # ========================================================
    # GENERATE HTML
    # ========================================================

    print()

    print(
        "Membuat halaman HTML..."
    )


    generate_html(data)


    # ========================================================
    # SELESAI
    # ========================================================

    print()

    print(
        "======================================"
    )

    print(
        "          PROSES SELESAI"
    )

    print(
        "======================================"

    )


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    main()