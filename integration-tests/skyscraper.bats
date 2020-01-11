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

@test "crawl example.com with scrapy spider" {
    python -m skyscraper --spider integration-tests/spiders/scrapy/example.yml
    count=$(ls /tmp/skyscraper-integration-tests/items/scrapy/example/ | wc -l)

    [ "$count" -eq 1 ]
}

@test "crawl example.com with configuration yml" {
    python -m skyscraper --spider integration-tests/spiders/test/examplecom.yml
    count=$(ls /tmp/skyscraper-integration-tests/items/test/examplecom/ | wc -l)

    [ "$count" -eq 1 ]
}

@test "crawl wikipedia articles with configuration yml" {
    python -m skyscraper --spider integration-tests/spiders/test/wikipedia.yml
    count_articles=$(ls /tmp/skyscraper-integration-tests/items/test/wikipedia/ | wc -l)
    count_images=$(ls /tmp/skyscraper-integration-tests/downloads/test/wikipedia/ | wc -l)

    [ "$count_articles" -gt 1 ]
    [ "$count_images" -ge 1 ]
}

@test "crawl example.com with Chrome headless" {
    python -m skyscraper --spider integration-tests/spiders/chrome/examplecom.yml
    count=$(ls /tmp/skyscraper-integration-tests/items/chrome/examplecom/ | wc -l)
    title=$(cat /tmp/skyscraper-integration-tests/items/chrome/examplecom/*.json | jq -r ".data.title")

    [ "$count" -eq 1 ]
    [ "$title" = "Example Domain" ]
}

@test "check TOR has different IP" {
    skyscraper-spider tor checkip --use-tor
    count=$(ls /tmp/skyscraper-integration-tests/items/tor/checkip/ | wc -l)

    [ "$count" -eq 1 ]

    spider_ip=$(cat /tmp/skyscraper-integration-tests/items/tor/checkip/*.json | jq -r '.data.ip')
    machine_ip=$(curl -s "https://api.ipify.org/?format=json" | jq -r '.ip')

    [ "$spider_ip" != "$machine_ip" ]
}
