class BetsCalculator {
    storageKey = 'cbets'
    bets
    stake
    newsCalculator = $('.news-calculator')
    singleHeaderEl = $('.single-text')
    multiHeaderEl = $('.multi-text')
    possibleWinningsEl = $('.amount.possible')
    stakeAmountEl = $(".stake-amount")
    placeBetEL = $('.placeBet')
    calcBody = $('.calculator-body')
    betsTable = $('.calculator-body__bets')
    calcResult = $('.calculator-result')
    calcAgreement = $('.agree.calc-agreement')

    constructor() {
        this.fetchData()
        this.rerender()
    }

    get active() {
        return Boolean(this.bets.length >= 1)
    }

    get mode() {
        return this.bets.length > 1 ? 'multi' : 'single'
    }

    get totalOdds() {
        return this.roundNumber(
            this.bets.reduce(
                (prev, bet) => prev * bet.koef, 1
            )
        )
    }

    get possibleWinnigs() {
        return this.roundNumber(this.totalOdds * this.stake)
    }

    roundNumber(n) {
        return Math.round((n + Number.EPSILON) * 100) / 100
    }

    betExist(bet) {
        return this.bets.findIndex((iBet) =>
            iBet.eventId === bet.eventId &&
            iBet.team === bet.team &&
            iBet.betType === bet.betType &&
            iBet.koef === bet.koef
        )
    }

    similarBetExist(bet) {
        return this.bets.findIndex((iBet) =>
            iBet.eventId === bet.eventId &&
            iBet.betType === bet.betType
        )
    }

    addBet(bet) {
        const similarBetIndex = this.similarBetExist(bet)
        if(similarBetIndex !== -1) {
            // check if there is bets on similar match with similar bet type

            if (this.betExist(bet) === -1) {
                // if exist similar bet on the same bet type replace it
                this.removeBet(similarBetIndex)
                this.bets.push(bet)
                this.upgradeData()
            }

            // if same bet already exist just go out
        } else {
            this.bets.push(bet)
            this.upgradeData()
        }
    }

    removeBet(index) {
        this.bets.splice(index, 1)
        this.upgradeData()
    }

    fetchData() {
        const data = JSON.parse(localStorage.getItem(this.storageKey))
        if (data) {
            this.stake = data.stake
            this.bets = data.bets
            this.upgradeData()

        } else {
            console.log('error')
            this.bets = []
            this.stake = 5
            this.upgradeData()
        }
    }

    upgradeData() {
        localStorage.setItem(this.storageKey, JSON.stringify({
            stake: this.stake,
            bets: this.bets
        }))
        this.rerender()
    }

    toggleBet(bet) {
        if (this.betExist(bet)) {
            this.addBet(bet)
        } else {
            this.removeBet(bet)
        }
    }

    addBetToTable = (bet, index) => {
        return $(`
        <div class="bet-item">
            <div class="bet-item__title">
                <p class="bet-item__title-match" id="match">${bet.match}</p>
                <div class="bet-item__title-right">
                    <div class="bet-item__title-right__odd" id="odd">${bet.koef}</div>
                    <div class="bet-item__title-right__remove" data-bet="${index}" id="remove-bet">
                        <span>&times;</span>
                    </div>
                </div>
            </div>
            <p class="bet-item__condition" id="type">${bet.betType}</p>
            <p class="bet-item__text" id="team">${bet.team}</p>
        </div>`)
    }

    changeStake = (number) => {
        this.stake = number
        this.upgradeData()
    }

    noSelectedBet = () => $(`<p class="no-bets">No bet has been selected. To select a bet, please click on the corresponding result.</p>`.trim())

    rerender = () => {
        if (this.active) {
            this.newsCalculator.show()
            if (this.mode === 'single') {
                this.singleHeaderEl.addClass('active')
                this.multiHeaderEl.removeClass('active')
            } else {
                this.multiHeaderEl.addClass('active')
                this.singleHeaderEl.removeClass('active')
            }
            this.betsTable.empty()
            this.bets.forEach((bet, index) => {
                const newRow = this.addBetToTable(bet, index);
                this.betsTable.append(newRow);
            })
            $('.no-bets').remove()
            this.calcResult.fadeIn()
            this.calcAgreement.fadeIn()
            this.betsTable.fadeIn()
            this.placeBetEL.fadeIn()
            this.stakeAmountEl.val(this.stake)
            this.possibleWinningsEl.text(this.possibleWinnigs + ' USD')
        } else {
            this.newsCalculator.hide()
            this.singleHeaderEl.removeClass('active');
            this.multiHeaderEl.removeClass('active');
            this.calcResult.fadeOut()
            this.calcAgreement.fadeOut()
            this.betsTable.fadeOut()
            this.placeBetEL.fadeOut()
            this.calcBody.append(this.noSelectedBet)
        }
    }

    placeBet() {
            // alarm require a license
    }

}
