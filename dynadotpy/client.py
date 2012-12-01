import requests


DELETE_RESPONSES = {
    "success": "The domain was successfully deleted",
    "grace_expired": "The grace period has already expired",
    "too_soon": "Cannot delete a domain the first hour after registration",
    "offline": "The central registry for this domain is currently offline",
    "error": "There was a syntax or registry error processing this request"
}

GET_NAMESERVERS_RESPONSES = {
    "success": "The nameservers were successfully return",
    "offline": "The central registry for this domain is currently offline",
    "error": "There was a syntax or registry error processing this request"
}

REGISTER_RESPONSES = {
    "success": "The domain was successfully registered",
    "not_available": "The domain is not available",
    "insufficient_funds": "Not enough account balance to process this "
        "registration",
    "offline": "The central registry for this domain is currently offline",
    "system_busy": "All connections are busy",
    "over_quota": "See quota details below",
    "error": "There was a syntax or registry error processing this request"
}

RENEW_RESPONSES = {
    "success": "The domain was successfully renewed",
    "insufficient_funds": "Not enough account balance to process this renewal",
    "offline": "The central registry for this domain is currently offline",
    "error": "There was a syntax or registry error processing this request"
}

SEARCH_RESPONSES = {
    "yes": "The domain is available.",
    "no": "The domain is not available.",
    "offline": "The central registry for this domain is currently offline.",
    "system_busy": "All connections are busy.",
    "over_quota": "Over quota.",
    "error": "There was a syntax or registry error processing this domain."
}

SET_FOLDER_RESPONSES = {
    "success": "The folder were successfully set",
    "error": "There was a syntax error processing this request"
}

SET_NAMESERVERS_RESPONSES = {
    "success": "The nameservers were successfully set",
    "offline": "The central registry for this domain is currently offline",
    "error": "There was a syntax or registry error processing this request"
}


class Dynadot(object):
    """A simple Python wrapper for the Dynadot.com API v2."""
    API_URL = "https://api.dynadot.com/api2.html"
    API_KEY = None
    RENEW_OPTIONS = ("reset", "donot", "auto")

    def __init__(self, api_key, *args, **kwargs):
        self.API_KEY = api_key
        self.payload = {"key": self.API_KEY}

    def delete(self, domain):
        """Delete a domain.

        ::
            >>> from dynadotpy.client import Dynadot
            >>> dyn = Dynadot(api_key="<key>")
            >>> result = dyn.delete(domain="example.com")
            {"result": u"success", "more_info": u""}

        :param domain: String of the domain.
        :return: `dict` of the response from Dynadot's API.
        """
        response = self._send_command(command="delete", domain=domain)

        if "error" in response:
            return self._error_response(response)

        return self._parse_delete_results(response[0].split(","))

    def get_nameservers(self, domain):
        """Get Nameservers for the given domain.

        ::
            >>> from dynadotpy.client import Dynadot
            >>> dyn = Dynadot(api_key="<key>")
            >>> result = dyn.get_nameservers(domain="example.com")
            {"result": u"success", "ns0": u"ns1.example.com"...

        :param: String of the domain.
        :return: `dict` of the response from Dynadot's API.
        """
        response = self._send_command(command="get_ns", domain=domain)

        if "error" in response:
            return self._error_response(response)

        return self._parse_get_nameservers_results(response[0].split(","))

    def register(self, domain, duration):
        """Register a domain.

        ::
            >>> from dynadotpy.client import Dynadot
            >>> dyn = Dynadot(api_key="<key>")
            >>> result = dyn.register(domain="example.com", duration=1)
            {"result": u"success", "expiration_date": "1180897681932"...

        :param: String of the domain you want to register.
        :param: String/int of the duration in years you wish to register.
        :return: `dict` of the response from Dynadot's API.
        """
        response = self._send_command(command="register", domain=domain,
            duration=duration)

        if "error" in response:
            return self._error_response(response)

        return self._parse_register_renew_results(response[0].split(","))

    def renew(self, domain, duration):
        """Renew a domain.

        ::
            >>> from dynadotpy.client import Dynadot
            >>> dyn = Dynadot(api_key="<key>")
            >>> result = dyn.renew(domain="example.com", duration=1)
            {"result": u"success", "expiration_date": "1180897681932"...

        :param: String of the domain you want to register.
        :param: String/int of the duration in years you wish to register.
        :return: `dict` of the response from Dynadot's API.
        """
        response = self._send_command(command="renew", domain=domain,
            duration=duration)

        if "error" in response:
            return self._error_response(response)

        return self._parse_register_renew_results(response[0].split(","))

    def search(self, domains):
        """Search for available domains.

        ::
            >>> from dynadotpy.client import Dynadot
            >>> dyn = Dynadot(api_key="<key>")
            >>> result = dyn.search(domains=["example.com",
                "example2.com"])
            [{'info': u'', 'domain': u'example.com', 'language': u'',
                'domain_param': u'domain0', 'result': u'no'}...]

        :param: `list` of domains you want to search for.
        :return: `list` of `dicts` for each domain searched.
        """
        if not isinstance(domains, list):
            raise TypeError("Search requires a [list] of domains.")

        if len(domains) > 100:
            raise Exception("Too many domain names. Dynadot only allows up to"
                "100 domains.")

        response = self._send_command(command="search",
            **{"domain%d" % num: domain for num, domain in enumerate(domains)})

        if "error" in response:
            return self._error_response(response)

        return self._parse_search_results(results=response)

    def set_folder(self, domain, folder):
        """
        Put specified domain in a named folder. You must create the
        folder on Dynadot's website before using this command.

        Note: folder names are case sensitive. Folder1 and folder1 are
        two different folder names.

        ::
            >>> from dynadotpy.client import Dynadot
            >>> dyn = Dynadot(api_key="<key>")
            >>> result = dyn.set_folder(domain="example.com",
                folder="folder1")
            {'result': 'success', 'more_info': ''}

        :param: String of the domain you want to move.
        :param: String of the folder you want to move the domain to.
        :return: `dict` of the response from Dynadot's API.
        """
        response = self._send_command(command="set_folder", domain=domain,
            folder=folder)

        if "error" in response:
            return self._error_response(response)

        return self._parse_set_folder_results(response[0].split(","))

    def set_nameservers(self, domain, nameservers):
        """Set nameservers for the given domain.

        ::
            >>> from dynadotpy.client import Dynadot
            >>> dyn = Dynadot(api_key="<key>")
            >>> result = dyn.set_nameservers(domain="example.com",
                nameservers=["ns1.example.com", "ns2.example.com"])
            {'result': 'success', 'more_info': ''}

        :param: String of the domain.
        :param: `list` of name servers you wish to set.
        :return: `dict` of the response from Dynadot's API.
        """
        if not isinstance(nameservers, list):
            raise TypeError("nameservers arg must be a [list].")

        if len(nameservers) > 13:
            raise Exception("Too many name servers. Dynadot only allows up to "
                "13 name servers.")

        response = self._send_command(command="set_ns", domain=domain,
            **{"ns%d" % num: ns for num, ns in enumerate(nameservers)})

        if "error" in response:
            return self._error_response(response)

        return self._parse_set_nameservers_results(response[0].split(","))

    def set_renew_option(self, domain, option):
        """Set domain renewal options.
        Valid options are:
            'reset': reset the domain's renew option to "no renew option"
            'donot': set the domain's renew option to "do not renew"
            'auto': set the domain's renew option to "auto-renew"

        ::
            >>> from dynadotpy.client import Dynadot
            >>> dyn = Dynadot(api_key="<key>")
            >>> result = dyn.set_renew_option(domain="example.com",
                option="auto")
            {'result': 'success', 'more_info': ''}

        :param: String of the domain.
        :param: String of the option you wish to set for the domain.
        :return: `dict` of the response from Dynadot's API.
        """
        if option not in self.RENEW_OPTIONS:
            raise Exception("Invalid renewal option. Options are: [%s]" % (
                ", ".join(self.RENEW_OPTIONS)))

        response = self._send_command(command="set_renew_option",
            domain=domain, option=option)

        if "error" in response:
            return self._error_response(response)

        return self._parse_set_renew_option_results(response[0].split(","))

    def _check_response_status(self, response):
        """Check response for errors."""
        response_list = response.split("\n")
        status = response_list[0].split(",")

        if "error" in status:
            return status

        return response_list[2:-1]

    def _error_response(self, response):
        """Return error responses."""
        return {response[0]: response[1]}

    def _parse_delete_results(self, result):
        """Parse delete result."""
        return {
            "result": result[0],
            "more_info": result[1]
        }

    def _parse_get_nameservers_results(self, result):
        """Parse nameserver result."""
        if result[0] != "success":
            return {"result": result[0], "more_info": result[1]}

        response = {"result": result[0], "more_info": result[14]}
        for n in xrange(0, 13):
            response.update({"ns%d" % n: result[n + 1]})

        return response

    def _parse_register_renew_results(self, result):
        """Parse registration result."""
        return {
            "result": result[0],
            "more_info": result[1],
            "expiration_date": result[2]
        }

    def _parse_search_results(self, results):
        """Parse search results."""
        search_results = []

        for result in results:
            result = result.split(",")
            if result:
                search_results.append({
                    "domain_param": result[0],
                    "domain": result[1],
                    "language": result[2],
                    "result": result[3],
                    "info": result[4]
                })
        return search_results

    def _parse_set_folder_results(self, result):
        """Parse set folder result."""
        return {
            "result": result[0],
            "more_info": result[1]
        }

    def _parse_set_nameservers_results(self, result):
        """Parse set name servers result."""
        return {
            "result": result[0],
            "more_info": result[1]
        }

    def _parse_set_renew_option_results(self, result):
        """Parse set renew option result."""
        return {
            "result": result[0],
            "more_info": result[1]
        }

    def _send_command(self, **kwargs):
        """
        Uses kwargs passed in to build a request to the Dynadot API.
        :returns: Response text
        """
        payload = self.payload.copy()
        payload.update(**kwargs)

        req = requests.get(self.API_URL, params=payload)
        return self._check_response_status(req.text)
