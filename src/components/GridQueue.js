export default class GridQueue {
  constructor(canvasReact) {
    this.canvasReact = canvasReact;
    this.queue = [];
  }
  async work() {
    while(true) {
      while (this.queue.length > 0) {
        var curTask = this.queue.shift();
        if (this.canvasReact.grids[curTask.size][curTask.x][curTask.y] == null)
        {
          var res = await fetch(get_grid_size_url + `${curTask.size}/${curTask.x}/${curTask.y}/`)
          res = await res.json();
          res = JSON.parse(res);
          this.canvasReact.grids[curTask.size][curTask.x][curTask.y] = res;
          this.canvasReact.forceUpdate();
        }
      }
      await sleep(500);
    }
  }
  append(x, y, size) {
  if (this.queue.length != 0) {
    if (this.queue[0].size != size) {
      this.queue = []
    }
  }
  this.queue.push({"x": x, "y": y, "size": size});
  }
};

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}