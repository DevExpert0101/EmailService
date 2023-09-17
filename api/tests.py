import datetime as dt

from django.test import TestCase

from email_finder.core.main import find_email


class EmailFinderTest(TestCase):
    def test_1(self):
        r = find_email("samuel", "", "beek", "veed.io").result
        self.assertTrue(
            "emails" in r
            and len(r["emails"]) == 2
            and "sam@veed.io" in r["emails"]
            and "s@veed.io" in r["emails"],
            f"Wrong result: {r}",
        )

    def test_2(self):
        r = find_email("charlie", "g", "kirkconnell", "caymanenterprisecity.com").result
        self.assertTrue(
            "emails" in r
            and len(r["emails"]) == 2
            and "cgk@caymanenterprisecity.com" in r["emails"]
            and "c.kirkconnell@caymanenterprisecity.com" in r["emails"],
            f"Wrong result: {r}",
        )

    def test_3(self):
        r = find_email("helen", "", "spiegel", "cima.ky").result
        self.assertTrue(
            "emails" in r and len(r["emails"]) == 1 and "helenspiegel@cima.ky" in r["emails"],
            f"Wrong result: {r}",
        )

    def test_4(self):
        r = find_email("jay", "", "mumtaz", "biizy.com").result
        self.assertTrue(
            "emails" in r and len(r["emails"]) == 1 and "j@biizy.com" in r["emails"],
            f"Wrong result: {r}",
        )

    def test_5(self):
        r = find_email("dylan", "", "bostock", "swpcayman.com").result
        self.assertTrue(
            "emails" in r and len(r["emails"]) == 1 and "db@swpcayman.com" in r["emails"],
            f"Wrong result: {r}",
        )

    def test_6(self):
        r = find_email("anna", "", "krendzelakova", "harneys.com").result
        self.assertTrue(
            "emails" in r
            and len(r["emails"]) == 1
            and "anna.krendzelakova@harneys.com" in r["emails"],
            f"Wrong result: {r}",
        )

    def test_7(self):
        r = find_email("anna", "", "ghandilyan", "artexrisk.com").result
        self.assertTrue(
            "emails" in r
            and len(r["emails"]) == 1
            and "anna_ghandilyan@artexrisk.com" in r["emails"],
            f"Wrong result: {r}",
        )

    def test_8(self):
        r = find_email("rahul", "", "swani", "aerispartners.com").result
        self.assertTrue(
            "emails" in r and len(r["emails"]) == 1 and "rs@aerispartners.com" in r["emails"],
            f"Wrong result: {r}",
        )

    def test_9(self):
        r = find_email("david", "w", "joncas", "aerispartners.com").result
        self.assertTrue(
            "emails" in r and "dwj@aerispartners.com" in r["emails"],
            f"Wrong result: {r}",
        )

    def test_10(self):
        r = find_email("george", "", "wauchope", "emailchaser.io").result
        self.assertTrue(
            "emails" in r and len(r["emails"]) == 1 and "george@emailchaser.io" in r["emails"],
            f"Wrong result: {r}",
        )

    def test_11(self):
        r = find_email("michael", "", "walsh", "cybersource.com").result
        self.assertTrue(
            "emails" in r,
            f"Wrong result: {r}",
        )

    def test_12(self):
        r = find_email("matthew", "", "lafferty", "curri.com").result
        self.assertTrue(
            "emails" in r and len(r["emails"]) == 3,
            f"Wrong result: {r}",
        )

    def test_13(self):
        r = find_email("jun", "", "rung", "envato.com").result
        self.assertTrue(
            "emails" in r and len(r["emails"]) == 2,
            f"Wrong result: {r}",
        )

    def test_14(self):
        start_time = dt.datetime.now()
        find_email("louise", "", "reed", "nova.ky")
        end_time = dt.datetime.now()
        self.assertTrue((end_time - start_time).seconds < 10, "Long time")

    def test_15(self):
        r = find_email("john", "", "doak", "johndoak.com").result
        self.assertTrue(
            "doak@johndoak.com" in r.get("emails", []),
            f"Wrong result: {r}",
        )
