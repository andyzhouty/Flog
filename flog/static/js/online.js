function ping_online() {
    axios({
        method: "get",
        url: "/ajax/ping_status/",
        headers: {
            "Accept": "application/json",
        },
        timeout: 10000,
        validateStatus: function (status) {
            return status == 200
        },
    }).catch(error => {}).then(function (response) {
        console.log("Connected with Server!")
        setTimeout("ping_online()", 30000)
    })
}

function get_all_status() {
    axios({
        method: "get",
        url: "/ajax/get_all_status/",
        headers: {
            "Accept": "application/json",
        },
        timeout: 10000,
        validateStatus: function (status) {
            return status == 200
        },
    }).catch(error => {
        console.log("Error pulling all status...")
        let r = error
    }).then(function (response) {
        setInterval("get_all_status()", 8000)
        console.log(response)
        let r = response
    })
    return r
}