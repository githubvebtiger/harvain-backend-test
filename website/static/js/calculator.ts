type CalculatorMode = 'single' | 'multi'

interface Bet {
    eventId: number,
    team: string,
    betType: string,
    match: string,
    koef: number
}

// calculator data
interface CBet {
    stake: number,
    bets: Bet[]
}

class BetsCalculator {
    private storageKey = 'cbets'
    private bets: Bet[]
    public stake: number

    constructor () {
        this.fetchData()
        this.rerender()
    }

    public get active() : boolean {
        return Boolean(this.bets.length)
    }

    public get mode() : CalculatorMode {
        return this.bets.length > 1 ? 'multi' : 'single'
    }

    public get totalOdds() : number {
        return this.roundNumber(
            this.bets.reduce<number>(
                (prev:number, bet:Bet) => prev * bet.koef, 1
            )
        )
    }

    public get possibleWinnigs () : number {
        return this.roundNumber(this.totalOdds * this.stake)
    }

    private roundNumber(n:number): number {
        return Math.round((n + Number.EPSILON) * 100) / 100
    }

    private betExist(bet:Bet): number {
        return this.bets.findIndex((iBet:Bet) =>
            iBet.eventId === bet.eventId &&
            iBet.team == bet.team &&
            iBet.betType == bet.betType &&
            iBet.team == bet.team &&
            iBet.koef == bet.koef
        )
    }

    private addBet(bet:Bet) {
        if(!this.betExist(bet)) {
            this.bets.push(bet)
            this.upgradeData()
        }
    }

    private removeBet(bet:Bet) {
        const betIndex = this.betExist(bet)
        if(betIndex == -1) return

        this.bets.splice(betIndex, 1)
        this.upgradeData()
    }

    private fetchData():CBet {
        try {
            const data = JSON.parse(localStorage.getItem(this.storageKey) || "") as CBet
            this.stake = data.stake
            this.bets = data.bets
        } catch (error) {
            this.bets = []
            this.stake = 5
            this.upgradeData()
        } finally {
            return {
                stake: this.stake,
                bets: this.bets
            }
        }
    }

    private upgradeData() {
        localStorage.setItem(this.storageKey, JSON.stringify({
            stake:this.stake,
            bets:this.bets
        }))
    }

    toggleBet (bet:Bet) {
        if(this.betExist(bet)) {
            this.addBet(bet)
        } else {
            this.removeBet(bet)
        }
        this.rerender()
    }

    rerender() {
        // rerender all parts of calculator here
        // if (this.active) {
        //     $('BetsCalculator').fadeOut()
        // } else {
        //     $('BetsCalculator').fadeIn()
        // }
    }

    placeBet () {
        // alarm require a license
    }
}
