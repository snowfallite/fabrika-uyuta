<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { COOKIE_NOTICE } from '$lib/content/layout';

	interface Props {
		/** The visitor already pressed OK: the cookie came with the request. */
		accepted: boolean;
		/** Where the no-JS form returns after the 303. */
		path: string;
	}

	let { accepted, path }: Props = $props();

	let dismissed = $state(false);

	function accept(event: SubmitEvent) {
		// With JS the cookie is set in the background and the page keeps its state.
		event.preventDefault();
		dismissed = true;
		void fetch('/cookie-consent', { method: 'POST', redirect: 'manual' });
	}
</script>

{#if !accepted && !dismissed}
	<!-- Sticky, not fixed: at the end of the page it steps aside and frees the footer links. -->
	<div class="sticky bottom-0 z-40 px-4 pb-4 sm:px-6 sm:pb-6">
		<section
			aria-label={COOKIE_NOTICE.label}
			class="mx-auto flex max-w-3xl flex-col gap-4 rounded-2xl border border-border bg-card p-5 shadow-float sm:flex-row sm:items-center sm:gap-6 sm:p-6"
		>
			<p class="text-sm leading-relaxed text-foreground/85">
				{COOKIE_NOTICE.textBefore}
				<a class="underline underline-offset-2" href="/cookies">{COOKIE_NOTICE.linkText}</a>
				{COOKIE_NOTICE.textAfter}
			</p>
			<form method="POST" action="/cookie-consent" class="shrink-0" onsubmit={accept}>
				<input type="hidden" name="redirectTo" value={path} />
				<Button type="submit" size="sm" class="px-8">{COOKIE_NOTICE.accept}</Button>
			</form>
		</section>
	</div>
{/if}
