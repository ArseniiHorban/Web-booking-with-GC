module.exports = {
    content: [ 
        './pages_app/templates/**/*.html',  
        './calendar_app/templates/**/*.html',
        './payment_app/templates/**/*.html',
    ],
    theme: {
        extend: {
            colors: {
            },
        },  // Extend Tailwind's default theme if needed
    },
    variants: {
        extend: {},
    },
    plugins: [],  // Add Tailwind plugins if needed
}