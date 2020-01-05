#!/usr/bin/env bats

setup() {
    rm -rf /tmp/skyscraper-integration-tests

    pyppeteer-install

    mkdir -p /tmp/skyscraper-integration-tests/spiders
    mkdir -p /tmp/skyscraper-integration-tests/items
}

teardown() {
    rm -rf /tmp/skyscraper-integration-tests
}

@test "run skyscraper with example repository" {
    skyscraper &

    # Give the process 30 seconds for execution, then stop it
    pid=$!
    sleep 30
    kill $pid

    count_scrapy=$(ls /tmp/skyscraper-integration-tests/items/onetime_spiders/example/ | wc -l)
    count_chrome=$(ls /tmp/skyscraper-integration-tests/items/chrome_headless/example/ | wc -l)

    [ "$count_scrapy" -ge 1 ]
    [ "$count_chrome" -ge 1 ]
}

@test "crawl example.com with spider from git" {
    skyscraper-spider onetime_spiders example
    count=$(ls /tmp/skyscraper-integration-tests/items/onetime_spiders/example/ | wc -l)

    [ "$count" -eq 1 ]
}

@test "crawl example.com with configuration yml" {
    skyscraper-spider-yml --yml-file integration-tests/spiders/test/examplecom.yml --folder /tmp/skyscraper-integration-tests/items
    count=$(ls /tmp/skyscraper-integration-tests/items/test/examplecom/ | wc -l)

    [ "$count" -eq 1 ]
}

@test "crawl wikipedia articles with configuration yml" {
    skyscraper-spider-yml --yml-file integration-tests/spiders/test/wikipedia.yml --folder /tmp/skyscraper-integration-tests/items
    count=$(ls /tmp/skyscraper-integration-tests/items/test/wikipedia/ | wc -l)

    [ "$count" -gt 1 ]
}

@test "crawl example.com with Chrome headless from git" {
    skyscraper-spider chrome_headless example --engine chrome
    count=$(ls /tmp/skyscraper-integration-tests/items/chrome_headless/example/ | wc -l)

    [ "$count" -eq 1 ]
}

@test "check TOR has different IP" {
    skyscraper-spider tor checkip --use-tor
    count=$(ls /tmp/skyscraper-integration-tests/items/tor/checkip/ | wc -l)

    [ "$count" -eq 1 ]

    spider_ip=$(cat /tmp/skyscraper-integration-tests/items/tor/checkip/*.json | jq -r '.data.ip')
    machine_ip=$(curl -s "https://api.ipify.org/?format=json" | jq -r '.ip')

    [ "$spider_ip" != "$machine_ip" ]
}
