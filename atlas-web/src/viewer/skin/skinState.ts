/** Skin owns no anatomy selection, other layers or camera state. */
export class SkinLayerState {
  visible = false;
  explicitOff = false;
  private beforeAcupoints: boolean | null = null;
  manual(visible: boolean) { this.visible = visible; this.explicitOff = !visible; }
  acupoints(active: boolean) {
    if (active && this.beforeAcupoints === null) {
      this.beforeAcupoints = this.visible;
      if (!this.explicitOff) this.visible = true;
    } else if (!active && this.beforeAcupoints !== null) {
      this.visible = this.beforeAcupoints;
      this.beforeAcupoints = null;
    }
  }
  suspend() { this.visible = false; }
}
