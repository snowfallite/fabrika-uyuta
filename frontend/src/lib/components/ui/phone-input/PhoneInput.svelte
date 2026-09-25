<script lang="ts">
	import { formatPhoneInput } from '$lib/domain/phone';
	import { fieldClass } from '../input/input.svelte';

	interface Props {
		name: string;
		id?: string;
		value?: string;
		required?: boolean;
		'aria-invalid'?: boolean;
		'aria-describedby'?: string;
	}

	let { value = $bindable(''), ...rest }: Props = $props();
</script>

<!-- Without JS the mask never runs and the field stays a plain tel input. -->
<input
	type="tel"
	inputmode="tel"
	autocomplete="tel"
	placeholder="+7 (___) ___-__-__"
	maxlength={32}
	class={fieldClass}
	{value}
	oninput={(event) => {
		value = formatPhoneInput(event.currentTarget.value);
		event.currentTarget.value = value;
	}}
	{...rest}
/>
