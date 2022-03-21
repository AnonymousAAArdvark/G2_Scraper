from pandas.io.excel import ExcelWriter
import pandas as pd
with ExcelWriter('data_review.xlsx') as ew:
	#将csv文件转换为excel文件
	pd.read_csv("review_data_full.csv").to_excel(ew, sheet_name="sheet1", index=False)
