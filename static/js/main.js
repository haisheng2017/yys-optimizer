/**
 * @author yitiaoxiangsugou
 */
const v1 = new Vue({
    el: '#app',
    vuetify: new Vuetify(),
    data: {
        newTargetNum: '',
        monsters: null,
        target: {},
        limitSize: 10,
        selected: '',
        hasResult: false,
        loaded: false,
        resultInfo: null,
        resultSize: 0,
        hasDiscovery: true,
        hasMonster: true,
        hasSnake: true,
        hasHighLevel: true,
        hasChallenge: false,
    },
    methods: {
        addNewTarget: function () {
            if (Object.keys(this.target).length >= this.limitSize ||
                this.selected.length === 0 || this.newTargetNum <= 0 || this.newTargetNum > 20) {
                return;
            }

            let targetNum = parseInt(this.newTargetNum);
            let targetName = this.selected;
            this.target[targetName] = targetNum;
            this.selected = ''
            this.newTargetNum = ''
        },
        remove: function (key) {
            this.$delete(this.target, key)
        },
        submit: function () {
            if (Object.keys(this.target).length === 0) {
                return
            }
            let lowLevel = this.hasHighLevel ? 0 : 5;
            let filter = this.hasHighLevel ? 0 : 1;
            filter = (filter << 1) | (this.hasMonster ? 0 : 1);
            filter = (filter << 1) | 1;
            let data = {
                'target': this.target,
                'filter': filter,
                'lowLevel': lowLevel,
            }
            axios.post('/computation', data)
                .then(function (response) {

                    v1.resultSize = response.data['playTimes'].length
                    v1.resultInfo = response.data;
                    v1.errored = response.data['status'] !== 1;
                }).catch(function (error) {
                v1.errored = true;
            }).finally(function () {
                v1.hasResult = true
            });
        },
    },
    mounted: function () {
        axios.get('/monsters')
            .then(function (response) {
                v1.monsters = response.data
            }).catch(function (error) {
        }).finally(function () {
            v1.loaded = true;
        });
    }
});