# Copyright (c) 2020 Sarthak Mittal
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

FIELD_TYPES = {
    "general": 0,
    "optional": 1,
    "amount": 2,
    "date": 3
}

FIELDS = dict()

FIELDS["document_number"] = FIELD_TYPES["general"]
FIELDS["contractor"] = FIELD_TYPES["general"]
FIELDS["tax_number"] = FIELD_TYPES["general"]
FIELDS["bank_account"] = FIELD_TYPES["general"]

FIELDS["issued_on"] = FIELD_TYPES["date"]
FIELDS["sale_date"] = FIELD_TYPES["date"]
FIELDS["date_of_payment"] = FIELD_TYPES["date"]

FIELDS["currency"] = FIELD_TYPES["general"]
FIELDS["net_amount"] = FIELD_TYPES["amount"]
FIELDS["gross_amount"] = FIELD_TYPES["amount"]

FIELDS["vat"] = FIELD_TYPES["optional"]
