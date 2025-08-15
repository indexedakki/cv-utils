import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import Header from "@/components/Header";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-400">
      <Header
        logo="https://asofttek.com/wp-content/uploads/2022/09/Asoft-logos-3.png"
        // topLinks={[
        //   { label: "Our experience", href: "#" },
        //   { label: "Overview", href: "#" },
        //   { label: "Insights", href: "#" },
        //   { label: "Blog", href: "#" },
        //   { label: "Newsroom", href: "#" },
        //   { label: "Careers", href: "#" },
        //   { label: "Contact us", href: "#" },
        // ]}
        // mainLinks={[
        //   { label: "AI", href: "#" },
        //   { label: "APPROACH", href: "#" },
        //   { label: "INDUSTRIES", href: "#" },
        //   { label: "SERVICES & SOLUTIONS", href: "#" },
        //   { label: "TRANSCEND", href: "#" },
        // ]}
      />
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl mb-6 shadow-lg">
              <span className="text-3xl">🚀</span>
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent mb-6">
              Campaign Generator
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
              Generate AI-powered recruitment campaigns with ease. Transform your hiring process with intelligent, personalized outreach.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 mb-16">
            <Card className="group hover:shadow-xl transition-all duration-300 border-0 shadow-lg bg-white/80 backdrop-blur-sm hover:-translate-y-1">
              <CardHeader className="pb-4">
                <div className="flex items-center space-x-3 mb-2">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center text-xl shadow-md">
                    🎯
                  </div>
                  <CardTitle className="text-lg font-semibold text-gray-800">Smart Campaign Creation</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 leading-relaxed">
                  Create targeted recruitment campaigns using AI. Just describe your requirements and let our system generate personalized outreach messages.
                </p>
              </CardContent>
            </Card>

            <Card className="group hover:shadow-xl transition-all duration-300 border-0 shadow-lg bg-white/80 backdrop-blur-sm hover:-translate-y-1">
              <CardHeader className="pb-4">
                <div className="flex items-center space-x-3 mb-2">
                  <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-green-600 rounded-lg flex items-center justify-center text-xl shadow-md">
                    📧
                  </div>
                  <CardTitle className="text-lg font-semibold text-gray-800">Email Generation</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 leading-relaxed">
                  Automatically generate professional recruitment emails tailored to specific roles, experience levels, and locations.
                </p>
              </CardContent>
            </Card>

            <Card className="group hover:shadow-xl transition-all duration-300 border-0 shadow-lg bg-white/80 backdrop-blur-sm hover:-translate-y-1">
              <CardHeader className="pb-4">
                <div className="flex items-center space-x-3 mb-2">
                  <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg flex items-center justify-center text-xl shadow-md">
                    👥
                  </div>
                  <CardTitle className="text-lg font-semibold text-gray-800">Candidate Management</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 leading-relaxed">
                  Track and manage candidates throughout the recruitment process with our integrated candidate management system.
                </p>
              </CardContent>
            </Card>

            <Card className="group hover:shadow-xl transition-all duration-300 border-0 shadow-lg bg-white/80 backdrop-blur-sm hover:-translate-y-1">
              <CardHeader className="pb-4">
                <div className="flex items-center space-x-3 mb-2">
                  <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg flex items-center justify-center text-xl shadow-md">
                    🤖
                  </div>
                  <CardTitle className="text-lg font-semibold text-gray-800">AI-Powered Conversations</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 leading-relaxed">
                  Interactive chat interface that guides you through the campaign creation process with intelligent questions and suggestions.
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="text-center mb-16">
            <Link href="/campaign">
              <Button
                size="lg"
                className="px-12 py-4 text-lg font-semibold bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5 rounded-xl"
              >
                Start Creating Campaign
                <span className="ml-2">→</span>
              </Button>
            </Link>
          </div>

          <div className="bg-white/60 backdrop-blur-sm rounded-3xl p-8 shadow-xl border border-white/20">
            <h3 className="text-2xl font-bold text-gray-800 mb-8 text-center">How it works</h3>
            <div className="space-y-6">
              <div className="flex items-start space-x-4 group">
                <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl flex items-center justify-center text-lg font-bold shadow-lg group-hover:scale-110 transition-transform duration-300">
                  1
                </div>
                <div className="pt-2">
                  <p className="text-gray-700 text-lg leading-relaxed">Describe your job requirements in natural language</p>
                </div>
              </div>
              <div className="flex items-start space-x-4 group">
                <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl flex items-center justify-center text-lg font-bold shadow-lg group-hover:scale-110 transition-transform duration-300">
                  2
                </div>
                <div className="pt-2">
                  <p className="text-gray-700 text-lg leading-relaxed">Our AI will ask clarifying questions to understand your needs</p>
                </div>
              </div>
              <div className="flex items-start space-x-4 group">
                <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-xl flex items-center justify-center text-lg font-bold shadow-lg group-hover:scale-110 transition-transform duration-300">
                  3
                </div>
                <div className="pt-2">
                  <p className="text-gray-700 text-lg leading-relaxed">Receive a personalized email draft for your campaign</p>
                </div>
              </div>
              <div className="flex items-start space-x-4 group">
                <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-xl flex items-center justify-center text-lg font-bold shadow-lg group-hover:scale-110 transition-transform duration-300">
                  4
                </div>
                <div className="pt-2">
                  <p className="text-gray-700 text-lg leading-relaxed">Review, edit, and send your campaign to candidates</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}