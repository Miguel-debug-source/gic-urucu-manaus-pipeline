import pandas as pd
import os

# --- Caminhos ---
kp_daily_file_path = "./data/raw/geomagnetic_indice/kp_diario/kp_daily_2016_2017.csv"
magnetometer_man_folder_path = "./data/raw/magnetometer/man"
processed_output_folder_path = "./outputs/processed"

# --- Configuração ---
kp_threshold = 24  # dia só conta se Kp_sum > 24
month_abbreviations_english = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
years_list = [2016, 2017]

# --- Leitura do Kp diário ---
daily_kp_table = pd.read_csv(kp_daily_file_path)

# Converte a coluna de texto "Date" para datetime de verdade
daily_kp_table["Date"] = pd.to_datetime(daily_kp_table["Date"])

# Cria colunas separadas de ano e mês, pra facilitar os filtros mais na frente
daily_kp_table["Year"] = daily_kp_table["Date"].dt.year
daily_kp_table["Month"] = daily_kp_table["Date"].dt.month

def check_if_magnetometer_file_exists(a_date):
    """Verifica se existe o arquivo bruto do magnetômetro de Manaus pra essa data."""
    two_digit_day = f"{a_date.day:02d}"
    month_abbreviation = month_abbreviations_english[a_date.month - 1]
    two_digit_year = str(a_date.year)[-2:]

    # Monta o nome do arquivo, no padrão da estação (ex: man06jul.16m)
    file_name = "man" + two_digit_day + month_abbreviation + "." + two_digit_year + "m"

    full_path = magnetometer_man_folder_path + "/" + str(a_date.year) + "/" + file_name
   
    return os.path.exists(full_path)

# --- 1. Conta quantos dias por mês tiveram Kp_sum > 24, separado por ano ---
days_above_threshold = daily_kp_table[daily_kp_table["Kp_sum"] > kp_threshold]

# Tabela cruzada: uma linha por mês, uma coluna por ano
monthly_count_table = pd.crosstab(days_above_threshold["Month"], days_above_threshold["Year"])
monthly_output_path = processed_output_folder_path + "/monthly_kp_above_24.csv"
monthly_count_table.to_csv(monthly_output_path)
print("Saved:", monthly_output_path)

# --- 2. Pra cada ano, salva os dias acima do limiar + se tem arquivo do magnetômetro ---
for a_year in years_list:
    # Filtra só os dias desse ano que passaram do limiar de Kp
    year_table = days_above_threshold[days_above_threshold["Year"] == a_year].reset_index(drop=True)

    #Marca, dia por dia, se existe o dado bruto do magnetômetro
    year_table["Has_Magnetometer_Data"] = year_table["Date"].apply(check_if_magnetometer_file_exists)

    # Mantém só as colunas relevantes pra saída
    table_to_save = year_table[["Date", "Kp_sum", "Has_Magnetometer_Data"]]

    output_file_name = "daily_kp_availability_" + str(a_year) + ".csv"
    output_path = processed_output_folder_path + "/" + output_file_name
    table_to_save.to_csv(output_path, index=False)
    print("Saved:", output_path)
