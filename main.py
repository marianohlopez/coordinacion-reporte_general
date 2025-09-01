import yagmail
from extract import (extract_general, extract_informes, extract_seguim, extract_prest, 
  extract_prest_sin_pa, extract_altas_bajas)
from transform import export_excel
from db import connect_db

def main():
    
    conn = connect_db()
    cursor = conn.cursor()
    general_data = extract_general(cursor)
    prest_sin_pa = extract_prest_sin_pa(cursor)
    informes_data = extract_informes(cursor)
    seguim_data = extract_seguim(cursor)
    prest_data = extract_prest(cursor)
    altas_bajas = extract_altas_bajas(cursor)
    export_excel(general_data, prest_sin_pa, informes_data, seguim_data, prest_data, altas_bajas)

if __name__ == "__main__":
  main()