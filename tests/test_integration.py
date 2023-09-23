import os
import resource
import pytest

from common import create_shell_pass, certs, resources


@pytest.mark.integration
def test_passbook_creation_integration():
    """
    This test can only run locally if you provide your personal Apple Wallet
    certificates, private key and password. It would not be wise to add
    them to git. Store them in the files indicated below, they are ignored
    by git.
    
    ATTENTION: in order to run this test you have to install the necessary certifcates in data/certs/private following the README.md
    these certificates are not provided in the repository for security reasons.
    
    this test opens the passbook file in the default application for .pkpass files )works only on OSX)
    """

    pass_file_name = "/Users/phil/dev/projects/edutap/apple/passes/pass1.pkpass"
    passfile = create_shell_pass(
        passTypeIdentifier="pass.demo.lmu.de", teamIdentifier="JG943677ZY"
    )
    passfile.addFile("icon.png", open(resources / "white_square.png", "rb"))

    zip = passfile.create(
        certs / "private" / "certificate.pem",
        certs / "private" / "private.key",
        certs / "private" / "wwdr_certificate.pem",
        "",
    )

    open(pass_file_name, "wb").write(zip.getvalue())
    os.system("open " + pass_file_name)
