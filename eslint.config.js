import salesforceLwc from "@salesforce/eslint-config-lwc/flat/recommended";
import lockerRecommended from "@locker/eslint-config-locker/flat/recommended";
import globals from "globals";

export default [
    {
        // Global ignores
        ignores: [
            "**/node_modules/**",
            "**/coverage/**",
            "**/dist/**",
            "**/.sfdx/**",
            "**/.sf/**"
        ]
    },
    {
        // Base configuration for all JS files
        languageOptions: {
            ecmaVersion: "latest",
            sourceType: "module",
            globals: {
                ...globals.browser,
                ...globals.es2021
            }
        }
    },
    // Salesforce LWC recommended config
    ...salesforceLwc,
    // Locker Service recommended config
    ...lockerRecommended,
    {
        // Custom rules (add overrides here if needed)
        rules: {}
    }
];
