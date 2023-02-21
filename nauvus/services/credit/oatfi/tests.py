import pytest

from nauvus.services.credit.oatfi.api import Oatfi

oatfi = Oatfi()


@pytest.mark.usefixtures("broker")
def test_save_broker(broker):
    # try saving without an email
    broker_email = broker.email
    broker.email = ""
    try:
        oatfi.save_broker(broker)
        assert False, "Expected an exception since no email was given"
    except Exception as e:
        print(e)
        assert True

    # add email back and save the broker
    broker.email = broker_email
    result1 = oatfi.save_broker(broker)
    assert result1

    biz = oatfi.get_business_information(broker.uid)
    assert biz["name"] == broker.name

    # update the business by changing the name
    old_name = broker.name
    new_name = "Broker Testing Update"
    broker.name = new_name
    result2 = oatfi.save_broker(broker)
    assert result2

    biz = oatfi.get_business_information(broker.uid)
    assert biz["name"] == new_name

    # update the business by setting it back
    broker.name = old_name
    result3 = oatfi.save_broker(broker)
    assert result3


@pytest.mark.usefixtures("carrier_user")
def test_save_carrier(carrier_user):
    result1 = oatfi.save_carrier(carrier_user)
    assert result1


@pytest.mark.usefixtures("broker", "carrier_user", "invoices")
def test_send_invoice_history(broker, carrier_user, invoices):
    oatfi.save_carrier(carrier_user)
    oatfi.save_broker(broker)

    test_invoices = invoices

    result = oatfi.send_invoice_history(invoices=test_invoices)

    assert result


@pytest.mark.usefixtures("broker", "carrier_user")
def test_get_business_information(broker):

    # try to get business info before the broker is saved.  this should create an error
    try:
        oatfi.get_business_information(broker)
    except Exception as e:
        # expected an exception as this business should not be in oatfi
        print(e)
        assert True

    oatfi.save_broker(broker)

    try:
        response = oatfi.get_business_information(broker.uid)
        assert response["name"] == broker.name
    except Exception as e:
        # this should not happen
        assert False, e


def test_get_broker_preapproval(broker):
    # strip the mc number
    broker_mcnumber = broker.mc_number
    broker.mc_number = ""
    oatfi.save_broker(broker)

    # check to see if the broker is preapproved, expected to be No
    preapproval = oatfi.get_broker_preapproval(broker)
    assert preapproval is False, "Expected preapproval to be False, but received True from oatfi"

    broker.mc_number = broker_mcnumber
    oatfi.save_broker(broker)

    # check to see if the broker is preapproved, expected to be yes
    preapproval = oatfi.get_broker_preapproval(broker)
    assert preapproval, "Expected preapproval to be True, but received False from oatfi"


@pytest.mark.usefixtures("unpaid_invoice", "load_settlement")
def test_get_and_accept_loan_offer(unpaid_invoice, load_settlement, invoices):
    unpaid_invoice.load_settlement = load_settlement

    # test account for stripe - tied to justin@nauvus.com
    unpaid_invoice.carrier_user.user.stripe_customer_id = "acct_1Lu1pBBdeZ77yAv7"

    oatfi.save_carrier(unpaid_invoice.carrier_user)
    oatfi.save_broker(unpaid_invoice.broker)

    # send invoice history
    # invoice_list = invoices
    invoice_list = []
    invoice_list.append(unpaid_invoice)
    assert oatfi.send_invoice_history(invoice_list)

    try:
        loan = oatfi.get_loan_offer(unpaid_invoice)
        assert loan.principal_amount_in_cents > 0, "Expected loan amount to be >0"

        # accept the loan
        payment = oatfi.accept_loan(loan)
        assert payment.amount_in_cents > 0, "Expected payment amount to be >0"
    except Exception as e:
        # this should not happen
        # TODO: need to fix this as .save is causing an error
        print(unpaid_invoice)
        assert False, f"Invoice: id: {unpaid_invoice.uid}, broker id: {unpaid_invoice.broker.uid}  Exception {e}"

    assert True


def test_repay_loan():
    # TODO: write test
    assert True
