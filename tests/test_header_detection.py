import unittest
import tempfile
from pathlib import Path
import pandas as pd
from data_io.input_reader import read_v1_workbook
from core.validation import validate_all

class HeaderDetection(unittest.TestCase):
    def setUp(self):
        self.data=read_v1_workbook('project_risk_template_v2_2.xlsx')
    def write(self,path,offsets):
        with pd.ExcelWriter(path,engine='openpyxl') as writer:
            for i,(sheet,df) in enumerate(self.data.items()):
                df.to_excel(writer,sheet_name=sheet,index=False,startrow=offsets[i%len(offsets)])
    def test_headers_in_different_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            for offsets in ([1],[2],[0,1,5,3]):
                path=Path(folder)/'case.xlsx';self.write(path,offsets)
                data=read_v1_workbook(path)
                self.assertEqual(len(data['Activities']),30)
                self.assertEqual(len(data['Risk_Register']),24)
                self.assertEqual(data['Project'].iloc[0]['Field'],'Project_ID')
                self.assertFalse([x for x in validate_all(data) if x.severity=='Error'])
    def test_missing_header_has_clear_message(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'bad.xlsx'
            self.data['Project']=self.data['Project'].rename(columns={'Value':'Wrong'})
            self.write(path,[1])
            with self.assertRaisesRegex(ValueError,"Worksheet 'Project'.*Required headers"):
                read_v1_workbook(path)
    def test_whitespace_in_headers(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'spaces.xlsx'
            self.data['Project']=self.data['Project'].rename(columns={'Field':' Field ','Value':' Value '})
            self.write(path,[1])
            self.assertIn('Value',read_v1_workbook(path)['Project'])
if __name__=='__main__':unittest.main()
