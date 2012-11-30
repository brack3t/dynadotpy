import requests


SEARCH_RESPONSES = {
    "yes": "The domain is available.",
    "no": "The domain is not available.",
    "offline": "The central registry for this domain is currently offline.",
    "system_busy": "All connections are busy.",
    "over_quota": "Over quota.",
    "error": "There was a syntax or registry error processing this domain."
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

DELETE_RESPONSES = {
    "success": "The domain was successfully deleted",
    "grace_expired": "The grace period has already expired",
    "too_soon": "Cannot delete a domain the first hour after registration",
    "offline": "The central registry for this domain is currently offline",
    "error": "There was a syntax or registry error processing this request"
}

RENEW_RESPONSES = {
    "success": "The domain was successfully renewed",
    "insufficient_funds": "Not enough account balance to process this renewal",
    "offline": "The central registry for this domain is currently offline",
    "error": "There was a syntax or registry error processing this request"
}

GET_NAMESERVERS_RESPONSES = {
    "success": "The nameservers were successfully return",
    "offline": "The central registry for this domain is currently offline",
    "error": "There was a syntax or registry error processing this request"
}

SET_NAMESERVERS_RESPONSES = {
    "success": "The nameservers were successfully set",
    "offline": "The central registry for this domain is currently offline",
    "error": "There was a syntax or registry error processing this request"
}


class Dynadot(object):
    API_URL = "https://api.dynadot.com/api2.html"
    API_KEY = None
    RENEW_OPTIONS = ("reset", "donot", "auto")

    def __init__(self, api_key, *args, **kwargs):
        self.API_KEY = api_key
        self.payload = {"key": self.API_KEY}

    def delete(self, domain):
        """Delete a domain."""
        response = self._send_command(command="delete", domain=domain)

        if "error" in response:
            return self._error_response(response)

        return self._parse_delete_results(response[0].split(","))

    def get_nameservers(self, domain):
        """Get Nameservers for domain."""
        response = self._send_command(command="get_ns", domain=domain)

        if "error" in response:
            return self._error_response(response)

        return self._parse_get_nameservers_results(response[0].split(","))

    def search(self, domains):
        """Search for available domains."""
        if not isinstance(domains, list):
            raise TypeError("Search requires a [list] of domains.")

        response = self._send_command(command="search",
            **{"domain%d" % num: domain for num, domain in enumerate(domains)})

        if "error" in response:
            return self._error_response(response)

        return self._parse_search_results(results=response)

    def register(self, domain, duration):
        """Register a domain."""
        response = self._send_command(command="register", domain=domain,
            duration=duration)

        if "error" in response:
            return self._error_response(response)

        return self._parse_register_renew_results(response[0].split(","))

    def renew(self, domain, duration):
        """Renew a domain."""
        response = self._send_command(command="renew", domain=domain,
            duration=duration)

        if "error" in response:
            return self._error_response(response)

        return self._parse_register_renew_results(response[0].split(","))

    def set_nameservers(self, domain, nameservers):
        """Set nameservers for the given domain."""
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
        """Set domain renewal options."""
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
        """OH SNAP"""
        payload = self.payload.copy()
        payload.update(**kwargs)

        req = requests.get(self.API_URL, params=payload)
        return self._check_response_status(req.text)
