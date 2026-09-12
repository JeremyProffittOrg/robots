"""Acceptance checks for the user's total physical-piece limit."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from verify import audit_purchased_pieces


def part(key,quantity,status='counted'):
    return {'id':key,'item':'Purchased component','quantity':quantity,'count_status':status}


class PurchasedPieceLimit(unittest.TestCase):
    def test_limit_counts_quantities_not_rows(self):
        self.assertTrue(audit_purchased_pieces([part('candidate',148)])['passed'])
        self.assertTrue(audit_purchased_pieces([part('motors',7),part('other',192)])['passed'])
        result=audit_purchased_pieces([part('motors',7),part('other',193)])
        self.assertFalse(result['passed'])
        self.assertEqual(result['known_pieces'],200)
        self.assertEqual(result['excess_known_pieces'],1)

    def test_unresolved_hardware_cannot_pass(self):
        result=audit_purchased_pieces([part('candidate',148),part('wiring','','unresolved')])
        self.assertFalse(result['passed'])
        self.assertEqual(result['excess_known_pieces'],0)
        self.assertEqual(result['unresolved_rows'],['wiring'])

    def test_invalid_quantities_cannot_reduce_the_total(self):
        for value in ['','-10','0','1.5','1e1',None]:
            with self.subTest(value=value):
                self.assertFalse(audit_purchased_pieces([part('item',value)])['passed'])

    def test_duplicate_or_missing_identity_fails(self):
        self.assertFalse(audit_purchased_pieces([part('same',2),part('same',3)])['passed'])
        self.assertFalse(audit_purchased_pieces([part('',2)])['passed'])
        self.assertFalse(audit_purchased_pieces([])['passed'])

    def test_unrecognized_status_cannot_bypass_count(self):
        self.assertFalse(audit_purchased_pieces([part('hardware',100,'ignored')])['passed'])
        self.assertFalse(audit_purchased_pieces([part('hardware',1,'unresolved')])['passed'])


if __name__=='__main__':
    unittest.main()
