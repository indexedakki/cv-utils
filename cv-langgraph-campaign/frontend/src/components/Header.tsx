import React from "react";
import { Globe, Search } from "lucide-react";

interface NavLink {
    label: string;
    href: string;
}

interface HeaderProps {
    logo: string;
    // topLinks: NavLink[];
    // mainLinks: NavLink[];
}

// const Header: React.FC<HeaderProps> = ({ logo, topLinks, mainLinks }) => {
const Header: React.FC<HeaderProps> = ({ logo }) => {
    return (
        <header className="bg-gray-800 text-white">
            {/* Top Nav */}
            <div className="max-w-7xl mx-auto flex justify-between items-center px-4 py-1 text-sm border-b border-gray-600">
                {/* Logo */}
                <div className="flex items-center space-x-2">
                    <img src={logo} alt="Logo" className="h-15 w-auto" />
                </div>
                <div className="flex ml-auto space-x-4">
                    <Search className="cursor-pointer hover:text-gray-300" />
                    <Globe className="cursor-pointer hover:text-gray-300" />
                </div>
                {/* Top Links */}
                {/* <nav className="flex items-center space-x-3">
                    {topLinks.map((link, index) => (
                        <React.Fragment key={link.label}>
                            <a href={link.href} className="hover:text-gray-300">
                                {link.label}
                            </a>
                            {index < topLinks.length - 1 && (
                                <span className="text-gray-500">|</span>
                            )}
                        </React.Fragment>
                    ))}
                </nav> */}
            </div>

            {/* Main Nav */}
            {/* <div className="max-w-7xl mx-auto flex justify-between items-center px-4 py-2">
                Main Links
                <nav className="flex items-center space-x-6 font-semibold">
                    {mainLinks.map((link) => (
                        <a key={link.label} href={link.href} className="hover:text-gray-300">
                            {link.label}
                        </a>
                    ))}
                </nav>

                Icons
                <div className="flex ml-auto space-x-4">
                    <Search className="cursor-pointer hover:text-gray-300" />
                    <Globe className="cursor-pointer hover:text-gray-300" />
                </div>
            </div> */}
        </header>
    );
};

export default Header;
