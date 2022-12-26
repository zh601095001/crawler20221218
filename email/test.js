const str = '<span class="odds2 ">8.5</span><span class="odds1 ">0.88</span>'

const res = str.match(/^<span class="odds2.*?">(.*?)<\/span>.*?$/)
console.log(res)
