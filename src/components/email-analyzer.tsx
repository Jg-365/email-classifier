import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { FileUpload } from "@/components/ui/file-upload";
import { ClassificationBadge } from "@/components/ui/classification-badge";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Alert,
  AlertDescription,
} from "@/components/ui/alert";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import {
  Loader2,
  Brain,
  MessageSquare,
  BarChart3,
  FileText,
  Type,
  CheckCircle,
  AlertCircle,
  Zap,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import {
  useEmailAnalysis,
  EmailAnalysisResult,
  EmailExamples,
} from "@/lib/api";

interface EmailStats {
  total: number;
  productive: number;
  nonproductive: number;
}

const EmailAnalyzer = () => {
  const [emailText, setEmailText] = useState("");
  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] =
    useState<EmailAnalysisResult | null>(null);
  const [emailStats, setEmailStats] = useState<EmailStats>({
    total: 0,
    productive: 0,
    nonproductive: 0,
  });
  const [activeTab, setActiveTab] =
    useState<string>("text");
  const [isConnected, setIsConnected] =
    useState<boolean>(false);
  const [examples, setExamples] =
    useState<EmailExamples | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { toast } = useToast();
  const {
    analyzeText,
    analyzeFile,
    healthCheck,
    getExamples,
  } = useEmailAnalysis();

  // Verificar conexão com o backend
  useEffect(() => {
    const checkConnection = async () => {
      try {
        await healthCheck();
        setIsConnected(true);

        // Carregar exemplos
        const exampleData = await getExamples();
        setExamples(exampleData);
      } catch (error) {
        setIsConnected(false);
        setError(
          error instanceof Error
            ? error.message
            : "Falha na conexão com o servidor"
        );
      }
    };

    checkConnection();
  }, []);

  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    setActiveTab("file");

    // Limpar texto quando arquivo é selecionado
    setEmailText("");

    toast({
      title: "Arquivo carregado",
      description: `${file.name} foi selecionado para análise.`,
    });
  };

  const handleFileRemove = () => {
    setSelectedFile(null);
    setEmailText("");
  };

  const handleExampleSelect = (exampleText: string) => {
    setEmailText(exampleText);
    setActiveTab("text");
    setSelectedFile(null);

    toast({
      title: "Exemplo carregado",
      description:
        "Exemplo foi inserido no campo de texto.",
    });
  };

  const analyzeEmail = async () => {
    if (!isConnected) {
      toast({
        title: "Conexão indisponível",
        description:
          "Não foi possível conectar ao servidor. Tente novamente.",
        variant: "destructive",
      });
      return;
    }

    if (!emailText.trim() && !selectedFile) {
      toast({
        title: "Conteúdo vazio",
        description:
          "Por favor, insira o texto do email ou faça upload de um arquivo.",
        variant: "destructive",
      });
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      let result: EmailAnalysisResult;

      if (selectedFile) {
        result = await analyzeFile(selectedFile);
      } else {
        result = await analyzeText(emailText);
      }

      setAnalysisResult(result);

      // Atualizar estatísticas
      const newStats = {
        total: emailStats.total + 1,
        productive:
          emailStats.productive +
          (result.classification === "Productive" ? 1 : 0),
        nonproductive:
          emailStats.nonproductive +
          (result.classification === "Non-Productive"
            ? 1
            : 0),
      };
      setEmailStats(newStats);

      toast({
        title: "Análise concluída",
        description: `Email classificado como ${
          result.classification
        } com ${Math.round(
          result.confidence * 100
        )}% de confiança.`,
      });
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Erro desconhecido";
      setError(errorMessage);

      toast({
        title: "Erro na análise",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetAnalysis = () => {
    setEmailText("");
    setSelectedFile(null);
    setAnalysisResult(null);
    setError(null);
  };

  const getClassificationColor = (
    classification: string
  ) => {
    return classification === "Productive"
      ? "text-green-600"
      : "text-orange-600";
  };

  const getClassificationIcon = (
    classification: string
  ) => {
    return classification === "Productive"
      ? CheckCircle
      : AlertCircle;
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold">
                  AI Email Classifier
                </h1>
                <p className="text-sm text-muted-foreground">
                  Classificação inteligente e respostas
                  automáticas para emails empresariais
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div
                className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs ${
                  isConnected
                    ? "bg-green-100 text-green-800"
                    : "bg-red-100 text-red-800"
                }`}
              >
                <div
                  className={`w-2 h-2 rounded-full ${
                    isConnected
                      ? "bg-green-500"
                      : "bg-red-500"
                  }`}
                />
                <span>
                  {isConnected ? "Online" : "Offline"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="grid gap-6">
          {/* Alerta de Conexão */}
          {!isConnected && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Não foi possível conectar ao servidor
                backend. Verifique se o serviço está
                rodando.
                {error && (
                  <span className="block mt-1 text-sm">
                    Erro: {error}
                  </span>
                )}
              </AlertDescription>
            </Alert>
          )}

          {/* Estatísticas */}
          {emailStats.total > 0 && (
            <Card className="animate-fade-in">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5" />
                  <span>Estatísticas de Análise</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {emailStats.total}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Total Analisados
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {emailStats.productive}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Produtivos
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">
                      {emailStats.nonproductive}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Não Produtivos
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Input do Email */}
          <Card>
            <CardHeader>
              <CardTitle>Análise de Email</CardTitle>
              <CardDescription>
                Insira o texto do email ou faça upload de um
                arquivo (.txt ou .pdf) para classificação
                automática
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Tabs
                value={activeTab}
                onValueChange={setActiveTab}
              >
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger
                    value="text"
                    className="flex items-center space-x-2"
                  >
                    <Type className="h-4 w-4" />
                    <span>Texto</span>
                  </TabsTrigger>
                  <TabsTrigger
                    value="file"
                    className="flex items-center space-x-2"
                  >
                    <FileText className="h-4 w-4" />
                    <span>Arquivo</span>
                  </TabsTrigger>
                  <TabsTrigger
                    value="examples"
                    className="flex items-center space-x-2"
                  >
                    <Zap className="h-4 w-4" />
                    <span>Exemplos</span>
                  </TabsTrigger>
                </TabsList>

                <TabsContent
                  value="text"
                  className="space-y-4"
                >
                  <div className="relative">
                    <Textarea
                      placeholder="Cole aqui o texto completo do email para análise automática..."
                      value={emailText}
                      onChange={(e) =>
                        setEmailText(e.target.value)
                      }
                      className="min-h-[150px] resize-none"
                    />
                    <div className="absolute bottom-2 right-2 text-xs text-muted-foreground">
                      {emailText.length} caracteres
                    </div>
                  </div>
                </TabsContent>

                <TabsContent
                  value="file"
                  className="space-y-4"
                >
                  <FileUpload
                    onFileSelect={handleFileSelect}
                    onFileRemove={handleFileRemove}
                    selectedFile={selectedFile}
                  />
                  {selectedFile && (
                    <div className="text-sm text-muted-foreground">
                      Arquivo selecionado:{" "}
                      <strong>{selectedFile.name}</strong> (
                      {(selectedFile.size / 1024).toFixed(
                        1
                      )}{" "}
                      KB)
                    </div>
                  )}
                </TabsContent>

                <TabsContent
                  value="examples"
                  className="space-y-4"
                >
                  {examples ? (
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium mb-2 text-green-700">
                          📧 Emails Produtivos (Requerem
                          Ação)
                        </h4>
                        <div className="space-y-2">
                          {examples.productive.map(
                            (example, index) => (
                              <div
                                key={index}
                                className="p-3 bg-green-50 border border-green-200 rounded-lg cursor-pointer hover:bg-green-100 transition-colors"
                                onClick={() =>
                                  handleExampleSelect(
                                    example
                                  )
                                }
                              >
                                <p className="text-sm">
                                  {example.length > 100
                                    ? example.substring(
                                        0,
                                        100
                                      ) + "..."
                                    : example}
                                </p>
                              </div>
                            )
                          )}
                        </div>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2 text-orange-700">
                          💬 Emails Não Produtivos
                          (Cortesia)
                        </h4>
                        <div className="space-y-2">
                          {examples.non_productive.map(
                            (example, index) => (
                              <div
                                key={index}
                                className="p-3 bg-orange-50 border border-orange-200 rounded-lg cursor-pointer hover:bg-orange-100 transition-colors"
                                onClick={() =>
                                  handleExampleSelect(
                                    example
                                  )
                                }
                              >
                                <p className="text-sm">
                                  {example.length > 100
                                    ? example.substring(
                                        0,
                                        100
                                      ) + "..."
                                    : example}
                                </p>
                              </div>
                            )
                          )}
                        </div>
                      </div>

                      <div className="text-xs text-muted-foreground">
                        💡 <strong>Dica:</strong> Clique em
                        qualquer exemplo para carregá-lo no
                        campo de texto
                      </div>
                    </div>
                  ) : (
                    <div className="text-center text-muted-foreground">
                      <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
                      <p>Carregando exemplos...</p>
                    </div>
                  )}
                </TabsContent>
              </Tabs>

              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    {error}
                  </AlertDescription>
                </Alert>
              )}

              <div className="flex space-x-3">
                <Button
                  onClick={analyzeEmail}
                  disabled={
                    isAnalyzing ||
                    (!emailText.trim() && !selectedFile) ||
                    !isConnected
                  }
                  className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analisando com IA...
                    </>
                  ) : (
                    <>
                      <Brain className="mr-2 h-4 w-4" />
                      Analisar com IA
                    </>
                  )}
                </Button>

                {(emailText || selectedFile) && (
                  <Button
                    variant="outline"
                    onClick={resetAnalysis}
                  >
                    Limpar
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Resultado da Análise */}
          {analysisResult && (
            <Card className="animate-slide-up border-l-4 border-l-blue-500">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {React.createElement(
                      getClassificationIcon(
                        analysisResult.classification
                      ),
                      {
                        className: `h-5 w-5 ${getClassificationColor(
                          analysisResult.classification
                        )}`,
                      }
                    )}
                    <span>Resultado da Análise IA</span>
                  </div>
                  <ClassificationBadge
                    type={
                      analysisResult.classification.toLowerCase() as
                        | "productive"
                        | "unproductive"
                    }
                  />
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Métricas principais */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
                    <div
                      className={`text-2xl font-bold ${getClassificationColor(
                        analysisResult.classification
                      )}`}
                    >
                      {analysisResult.classification}
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">
                      Classificação
                    </div>
                  </div>

                  <div className="text-center p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {Math.round(
                        analysisResult.confidence * 100
                      )}
                      %
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">
                      Confiança
                    </div>
                  </div>

                  <div className="text-center p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {analysisResult.analysis.word_count}
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">
                      Palavras
                    </div>
                  </div>
                </div>

                {/* Barra de confiança */}
                <div>
                  <h4 className="font-medium mb-2">
                    Nível de Confiança
                  </h4>
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-3">
                      <div
                        className={`h-3 rounded-full transition-all duration-1000 ${
                          analysisResult.confidence > 0.8
                            ? "bg-gradient-to-r from-green-400 to-green-600"
                            : analysisResult.confidence >
                              0.6
                            ? "bg-gradient-to-r from-yellow-400 to-orange-500"
                            : "bg-gradient-to-r from-red-400 to-red-600"
                        }`}
                        style={{
                          width: `${
                            analysisResult.confidence * 100
                          }%`,
                        }}
                      />
                    </div>
                    <span className="text-sm font-medium">
                      {Math.round(
                        analysisResult.confidence * 100
                      )}
                      %
                    </span>
                  </div>
                </div>

                {/* Detalhes técnicos */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium mb-2">
                      Análise Textual
                    </h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">
                          Caracteres:
                        </span>
                        <span>
                          {
                            analysisResult.analysis
                              .text_length
                          }
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">
                          Palavras totais:
                        </span>
                        <span>
                          {
                            analysisResult.analysis
                              .word_count
                          }
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">
                          Palavras processadas:
                        </span>
                        <span>
                          {
                            analysisResult.analysis
                              .processed_words
                          }
                        </span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium mb-2">
                      Texto Processado
                    </h4>
                    <div className="bg-gray-50 p-3 rounded-lg text-xs text-gray-600 max-h-20 overflow-y-auto">
                      {analysisResult.processed_text ||
                        "Processamento não disponível"}
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Resposta sugerida */}
                <div>
                  <h4 className="font-medium mb-3 flex items-center space-x-2">
                    <MessageSquare className="h-4 w-4" />
                    <span>
                      Resposta Automática Sugerida
                    </span>
                  </h4>
                  <div
                    className={`rounded-lg p-4 border-l-4 ${
                      analysisResult.classification ===
                      "Productive"
                        ? "bg-green-50 border-l-green-500"
                        : "bg-orange-50 border-l-orange-500"
                    }`}
                  >
                    <p className="text-sm leading-relaxed">
                      {analysisResult.suggested_response}
                    </p>
                    <div className="mt-3 flex justify-end">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          navigator.clipboard.writeText(
                            analysisResult.suggested_response
                          );
                          toast({
                            title: "Copiado!",
                            description:
                              "Resposta copiada para a área de transferência.",
                          });
                        }}
                      >
                        Copiar resposta
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Texto original (resumo) */}
                <div>
                  <h4 className="font-medium mb-2">
                    Texto Original (Resumo)
                  </h4>
                  <div className="bg-gray-50 p-3 rounded-lg text-sm text-gray-700 max-h-32 overflow-y-auto">
                    {analysisResult.original_text}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default EmailAnalyzer;
