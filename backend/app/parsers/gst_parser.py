# GST parser - JSON/PDF extraction
import json
from typing import Dict, List
class GSTParser:
    def parse(self,file_path:str)->Dict:
        with open(file_path,'r') as f:
            data = json.load(f)
        if 'b2b' in data and 'b2cs' in data:
            return self._parse_gstr1(data)
        elif 'sup_details' in data:
            return self._parse_gstr3b(data)
        elif 'docdata' in data:
            return self._parse_gstr2b(data)
        else:
            raise ValueError("Unknown GST return Format")

    def _parse_gstr1(self, data: Dict) -> Dict:
        """Parse GSTR-1 (Outward/Sales)."""
        invoices = []
        
        # Loop through B2B (business-to-business) sales
        for supplier in data.get('b2b', []):
            ctin = supplier.get('ctin')  # Customer GSTIN
            
            for inv in supplier.get('inv', []):
                itm = inv.get('itms', [{}])[0].get('itm_det', {})
                invoices.append({
                    "ctin": ctin,
                    "invoice_no": inv.get('inum'),
                    "date": inv.get('idt'),
                    "value": inv.get('val', 0),
                    "taxable": itm.get('txval', 0),
                    "cgst": itm.get('camt', 0),
                    "sgst": itm.get('samt', 0),
                    "igst": itm.get('iamt', 0)
                })
        
        return {
            "type": "GSTR-1",
            "period": data.get('fp'),
            "gstin": data.get('gstin'),
            "b2b_invoices": invoices,
            "total_taxable": sum(i['taxable'] for i in invoices)
        }


    def _parse_gstr3b(self, data: Dict) -> Dict:
        """Parse GSTR-3B (Summary Return)."""
        sup = data.get('sup_details', {}).get('osup_det', {})
        itc_net = data.get('itc_elg', {}).get('itc_net', {})
        
        # Summing up reversals just for info
        itc_rev_list = data.get('itc_elg', {}).get('itc_rev', [])
        total_reversed = 0
        for item in itc_rev_list:
            total_reversed += item.get('iamt', 0) + item.get('camt', 0) + item.get('samt', 0)

        return {
            "type": "GSTR-3B",
            "period": data.get('ret_period'),
            "gstin": data.get('gstin'),
            "outward_taxable": sup.get('txval', 0),
            "output_tax": sup.get('iamt', 0) + sup.get('camt', 0) + sup.get('samt', 0),
            "itc_available": itc_net.get('iamt', 0) + itc_net.get('camt', 0) + itc_net.get('samt', 0),
            "itc_reversed": total_reversed
        }
    def _parse_gstr2b(self, data: Dict) -> Dict:
        """Parse GSTR-2B (Auto-drafted Input Tax Credit)."""
        invoices = []
        
        # Loop through suppliers
        for supplier in data.get('docdata', {}).get('b2b', []):
            ctin = supplier.get('ctin')
            name = supplier.get('trdnm')
            
            for inv in supplier.get('inv', []):
                itm = inv.get('itms', [{}])[0].get('itm_det', {})
                invoices.append({
                    "supplier_gstin": ctin,
                    "supplier_name": name,
                    "invoice_no": inv.get('inum'),
                    "date": inv.get('idt'),
                    "taxable": itm.get('txval', 0),
                    "total_tax": itm.get('iamt', 0) + itm.get('camt', 0) + itm.get('samt', 0)
                })
        
        return {
            "type": "GSTR-2B",
            "period": data.get('fp'),
            "gstin": data.get('gstin'),
            "inward_invoices": invoices,
            "total_itc_claimable": sum(i['total_tax'] for i in invoices)
        }