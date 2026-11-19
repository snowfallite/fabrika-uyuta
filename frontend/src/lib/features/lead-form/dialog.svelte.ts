/** Shared state of the lead dialog; only click handlers change it, so SSR keeps defaults. */
class LeadDialog {
	isOpen = $state(false);
	/** Slug of the category whose CTA opened the dialog, "" for a blank form (tech.md, 12.1). */
	product = $state('');

	open(product = '') {
		this.product = product;
		this.isOpen = true;
	}

	close() {
		this.isOpen = false;
	}
}

export const leadDialog = new LeadDialog();

/** CTA click: open the dialog, but leave new-tab clicks and no-JS navigation to /lead alone. */
export function openFromLink(event: MouseEvent, product = '') {
	if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
		return;
	}
	event.preventDefault();
	leadDialog.open(product);
}
