import React from 'react';
import { Button, Result } from 'antd';
import { FallbackProps } from 'react-error-boundary';

const ErrorFallback: React.FC<FallbackProps> = ({ error, resetErrorBoundary }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Result
        status="error"
        title="应用出错"
        subTitle={error.message || '未知错误'}
        extra={[
          <Button type="primary" key="console" onClick={resetErrorBoundary}>
            重试
          </Button>,
          <Button key="home" onClick={() => window.location.href = '/'}>
            返回首页
          </Button>,
        ]}
      />
    </div>
  );
};

export default ErrorFallback;