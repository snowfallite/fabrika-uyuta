<script lang="ts">
	interface Props {
		class?: string;
	}

	// White VK monogram from the official logo (vk.company/data/VK-logo/, tech.md v9).
	// The 160x160 viewBox keeps the clear space the logo squircle gives the monogram.
	let { class: className }: Props = $props();
</script>

<svg
	class={className}
	viewBox="0 0 160 160"
	fill="currentColor"
	aria-hidden="true"
	focusable="false"
	xmlns="http://www.w3.org/2000/svg"
>
	<path
		d="M85.857 115.359C49.7802 115.359 27.8859 90.3289 27.0347 48.7354H45.3067C45.8763 79.2889 59.7771 92.2553 70.4331 94.8985V48.7354H87.9499V75.0969C98.2283 73.9577 108.98 61.9641 112.603 48.7354H129.825C127.067 65.0105 115.361 77.0042 107.079 81.9514C115.361 85.9514 128.686 96.4217 133.825 115.359H114.887C110.887 102.7 101.083 92.8953 87.9499 91.5641V115.359H85.857Z"
	/>
</svg>
